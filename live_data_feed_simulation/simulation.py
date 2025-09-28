"""TRIAXUS CNV file live-feed simulator.

This module simulates a Sea-Bird CTD/aux sensors data stream and writes a
realistic-looking .cnv file on disk, complete with a header block and rows of
data at a configurable rate. It includes an interactive map UI, CLI and a
non-interactive mode for automated runs.
"""

import argparse
import os
import random
import threading
import time
import sys
import math
import json
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from collections import deque
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Callable


# --- CNV schema based on example file (17 variables) ---
# Names appear in the header and define the order of columns produced below.
NAME_LIST = [
    "t090C: Temperature [ITS-90, deg C]",
    "c0S/m: Conductivity [S/m]",
    "prDM: Pressure, Digiquartz [db]",
    "t190C: Temperature, 2 [ITS-90, deg C]",
    "c1S/m: Conductivity, 2 [S/m]",
    "sbeox0Mm/L: Oxygen, SBE 43 [umol/l]",
    "sbeox1Mm/L: Oxygen, SBE 43, 2 [umol/l]",
    "par: PAR/Irradiance, Biospherical/Licor [umol photons/m^2/sec]",
    "CStarTr0: Beam Transmission, WET Labs C-Star [%]",
    "sal00: Salinity, Practical [PSU]",
    "sal11: Salinity, Practical, 2 [PSU]",
    "scan: Scan Count",
    "timeS: Time, Elapsed [seconds]",
    "pumps: Pump Status",
    "latitude: Latitude [deg]",
    "longitude: Longitude [deg]",
    "flag: 0.000e+00",
]

# Min/max spans derived from the sample header. These bounds are used to:
# - format header "span" lines for each variable; and
# - constrain the random-walk generator for realistic values.
SPAN_MIN = [
    12.3276,
    4.055418,
    1.956,
    12.3361,
    4.055566,
    172.359,
    168.476,
    1.0e-12,
    84.6324,
    35.0889,
    35.0814,
    1,
    0.0,
    1,
    -35.57462,
    154.30952,
    0.0,
]

SPAN_MAX = [
    21.6890,
    5.027629,
    292.795,
    21.6988,
    5.027419,
    253.438,
    247.188,
    3.2782e-05,
    98.2135,
    35.8769,
    35.8393,
    304611,
    12692.083,
    1,
    -35.20616,
    154.33126,
    0.0,
]

# Value used by Sea-Bird tools to mark missing/bad data; included in header.
BAD_FLAG = -9.990e-29


# Minimal offline city/port lookup for convenience (no network dependency).
# Note: This is intentionally small; extend as needed.
CITY_COORDS = {
    # Australia
    "sydney": (-33.8688, 151.2093),
    "melbourne": (-37.8136, 144.9631),
    "brisbane": (-27.4698, 153.0251),
    "perth": (-31.9523, 115.8613),
    "fremantle": (-32.0569, 115.7439),
    "adelaide": (-34.9285, 138.6007),
    "hobart": (-42.8821, 147.3272),
    "darwin": (-12.4634, 130.8456),
    # NZ
    "auckland": (-36.8485, 174.7633),
    "wellington": (-41.2865, 174.7762),
    "christchurch": (-43.5321, 172.6362),
    # World sample ports
    "singapore": (1.3521, 103.8198),
    "hong kong": (22.3193, 114.1694),
    "tokyo": (35.6762, 139.6503),
    "shanghai": (31.2304, 121.4737),
    "los angeles": (34.0522, -118.2437),
    "san francisco": (37.7749, -122.4194),
    "new york": (40.7128, -74.0060),
    "miami": (25.7617, -80.1918),
    "london": (51.5072, -0.1276),
    "hamburg": (53.5511, 9.9937),
    "rotterdam": (51.9244, 4.4777),
}

# Variable name helpers
VAR_KEYS = [name.split(":")[0] for name in NAME_LIST]
VAR_INDEX = {k: i for i, k in enumerate(VAR_KEYS)}
VAR_INDEX_LC = {k.lower(): i for k, i in VAR_INDEX.items()}




def _deg_to_degmin_str(lat_deg: float, lon_deg: float) -> Tuple[str, str]:
    """Convert decimal degrees to NMEA-like "DD MM.mm H" strings.

    Example: -35.57462 -> "35 34.48 S"
    """
    def one(val: float, pos_hem: str, neg_hem: str) -> str:
        hem = pos_hem if val >= 0 else neg_hem
        aval = abs(val)
        deg = int(aval)
        minutes = (aval - deg) * 60.0
        return f"{deg} {minutes:05.2f} {hem}"

    return one(lat_deg, "N", "S"), one(lon_deg, "E", "W")


def _utc_now_localstr() -> str:
    """Return current UTC timestamp formatted like the CNV headers expect."""
    return datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S")


def _run_route_picker_and_wait(cnv_path: Optional[str] = None, timeout_sec: float = 600.0):
    """Start a tiny local server, open a browser map, and wait for a route.

    Returns a dict with keys start_lat, start_lon, end_lat, end_lon or None on timeout.
    """
    doc_root = Path(__file__).resolve().parent
    html_file = doc_root / "route_picker.html"
    if not html_file.exists():
        alt = doc_root / "offline" / "route_picker.html"
        if alt.exists():
            html_file = alt
            doc_root = alt.parent
        else:
            print(f"[route] Missing {html_file}; cannot open route picker.")
            return None

    state = {
        "event": threading.Event(),
        "selection": None,
        "doc_root": str(doc_root),
        "rows": deque(maxlen=10000),
        "lock": threading.Lock(),
        "cnv_path": cnv_path,
    }

    class Handler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Quieter server
            pass
        def translate_path(self, path):
            # Serve files from doc_root regardless of CWD
            root = Path(state["doc_root"]).resolve()
            # default behavior but rooted
            rel = path.lstrip("/")
            safe = Path(rel)
            return str((root / safe).resolve())
        def do_POST(self):
            if self.path == "/set_route":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(length)
                    obj = json.loads(raw.decode("utf-8"))
                    s = obj.get("start") or {}
                    e = obj.get("end") or {}
                    sp = obj.get("speed_knots")
                    sel = {
                        "start_lat": float(s.get("lat")),
                        "start_lon": float(s.get("lon")),
                        "end_lat": float(e.get("lat")),
                        "end_lon": float(e.get("lon")),
                    }
                    if any(v is None for v in sel.values()):
                        raise ValueError("missing")
                    if sp is not None:
                        try:
                            sel["speed_knots"] = float(sp)
                        except Exception:
                            pass
                    state["selection"] = sel
                    state["event"].set()
                    # Call reroute callback and ensure writer is running
                    try:
                        cb = globals().get("_ROUTE_REROUTE_CB")
                        if cb:
                            cb(sel)
                    except Exception:
                        pass
                    try:
                        ctrl = globals().get("_ROUTE_CONTROL_CB")
                        if ctrl:
                            ctrl("resume")
                    except Exception:
                        pass
                    out = json.dumps({"ok": True}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(out)))
                    self.end_headers()
                    self.wfile.write(out)
                except Exception:
                    self.send_response(400)
                    self.end_headers()
            elif self.path == "/control/pause":
                try:
                    cb = globals().get("_ROUTE_CONTROL_CB")
                    if cb:
                        cb("pause")
                    out = json.dumps({"ok": True, "action": "pause"}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(out)))
                    self.end_headers()
                    self.wfile.write(out)
                except Exception:
                    self.send_response(500)
                    self.end_headers()
            elif self.path == "/control/resume":
                try:
                    cb = globals().get("_ROUTE_CONTROL_CB")
                    if cb:
                        cb("resume")
                    out = json.dumps({"ok": True, "action": "resume"}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(out)))
                    self.end_headers()
                    self.wfile.write(out)
                except Exception:
                    self.send_response(500)
                    self.end_headers()
            elif self.path == "/control/clear":
                try:
                    cb = globals().get("_ROUTE_CONTROL_CB")
                    if cb:
                        cb("clear")
                    out = json.dumps({"ok": True, "action": "clear"}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(out)))
                    self.end_headers()
                    self.wfile.write(out)
                except Exception:
                    self.send_response(500)
                    self.end_headers()
            elif self.path == "/control/speed":
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(length)
                    obj = json.loads(raw.decode("utf-8"))
                    val = float(obj.get("speed_knots"))
                    cb = globals().get("_ROUTE_SET_SPEED_CB")
                    if cb:
                        cb(val)
                    out = json.dumps({"ok": True, "action": "speed", "speed_knots": val}).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(out)))
                    self.end_headers()
                    self.wfile.write(out)
                except Exception:
                    self.send_response(400)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/bootstrap":
                # Try to read last lat/lon from existing CNV file if provided
                path = state.get("cnv_path")
                result = {"has_start": False}
                try:
                    if path and os.path.exists(path):
                        last_lat, last_lon = _read_last_lat_lon(path)
                        if last_lat is not None and last_lon is not None:
                            result = {"has_start": True, "start_lat": last_lat, "start_lon": last_lon}
                except Exception:
                    result = {"has_start": False}
                out = json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)
                return
            if parsed.path == "/live/status":
                with state["lock"]:
                    last_scan = 0
                    if state["rows"]:
                        try:
                            last_scan = int(state["rows"][-1][VAR_INDEX["scan"]])
                        except Exception:
                            last_scan = 0
                    out = json.dumps({
                        "ok": True,
                        "rows": len(state["rows"]),
                        "last_scan": last_scan,
                    }).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)
                return
            if parsed.path == "/live/latest":
                with state["lock"]:
                    if not state["rows"]:
                        self.send_response(204)
                        self.end_headers()
                        return
                    obj = _row_to_obj(state["rows"][-1])
                    out = json.dumps(obj).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)
                return
            if parsed.path == "/live/after":
                qs = parse_qs(parsed.query or "")
                try:
                    after_scan = int(qs.get("scan", [0])[0])
                except Exception:
                    after_scan = 0
                try:
                    max_rows = int(qs.get("max", [200])[0])
                except Exception:
                    max_rows = 200
                with state["lock"]:
                    result = []
                    for r in state["rows"]:
                        try:
                            sc = int(r[VAR_INDEX["scan"]])
                        except Exception:
                            sc = 0
                        if sc > after_scan:
                            result.append(_row_to_obj(r))
                    if len(result) > max_rows:
                        result = result[-max_rows:]
                    out = json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)
                return
            # default: static file
            return super().do_GET()

    # Bind to an available port on localhost
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = httpd.server_address[1]

    def run_server():
        try:
            httpd.serve_forever(poll_interval=0.2)
        except Exception:
            pass

    thr = threading.Thread(target=run_server, daemon=True)
    thr.start()

    url = f"http://127.0.0.1:{port}/route_picker.html"
    print(f"[route] Opening map: {url}")
    try:
        webbrowser.open(url)
    except Exception:
        print("[route] Could not open browser automatically. Open the URL manually.")
    # Wait for selection or timeout
    got = state["event"].wait(timeout=timeout_sec)
    # Do not shut down here; keep server alive for live view
    if not got:
        print("[route] Route picker timed out.")
        return None
    # Expose state to on_row callback via module global
    global _ROUTE_LIVE_STATE
    _ROUTE_LIVE_STATE = state
    return state["selection"]


def _format_header(
    file_hex_path: str,
    operator: str = "Scott",
    ship: str = "Investigator",
    cruise: str = "in2020_v09",
    station: str = "7",
    start_lat: float = -35.57462,
    start_lon: float = 154.30952,
    interval_sec: float = 0.0416667,
    start_time_utc: Optional[datetime] = None,
) -> str:
    """Build a realistic CNV header string.

    The header mirrors the structure of Sea-Bird Seasave output, including
    instrument metadata, variable schema, spans, and a sensors block copied as
    comments for realism. The resulting string ends with "*END*" and a newline.
    """
    dt_utc = start_time_utc or datetime.now(timezone.utc)
    sys_upload_time = dt_utc.strftime("%b %d %Y %H:%M:%S")
    nmea_time = dt_utc.strftime("%b %d %Y  %H:%M:%S")
    system_utc = dt_utc.strftime("%b %d %Y %H:%M:%S")
    start_time_line = dt_utc.strftime("%b %d %Y %H:%M:%S")
    nmea_lat_str, nmea_lon_str = _deg_to_degmin_str(start_lat, start_lon)

    lines: List[str] = []
    lines.append("* Sea-Bird SBE 9 Data File:")
    lines.append(f"* FileName = {file_hex_path}")
    lines.append("* Software Version Seasave V 7.26.7.110")
    lines.append("* Temperature SN = 5932")
    lines.append("* Conductivity SN = 3168")
    lines.append("* Number of Bytes Per Scan = 41")
    lines.append("* Number of Voltage Words = 4")
    lines.append("* Number of Scans Averaged by the Deck Unit = 1")
    lines.append("* Append System Time to Every Scan")
    lines.append(f"* System UpLoad Time = {sys_upload_time}")
    lines.append(f"* NMEA Latitude = {nmea_lat_str}")
    lines.append(f"* NMEA Longitude = {nmea_lon_str}")
    lines.append(f"* NMEA UTC (Time) = {nmea_time}")
    lines.append("* Store Lat/Lon Data = Append to Every Scan")
    lines.append(f"** Operator: {operator}")
    lines.append("** CTD config:")
    lines.append(f"** Ship: {ship}")
    lines.append(f"** Cruise: {cruise}")
    lines.append(f"** Station:  {station}")
    lines.append("** Latitude:")
    lines.append("** Longitude:")
    lines.append("** Depth:")
    lines.append(f"* System UTC = {system_utc}")

    # Schema
    lines.append(f"# nquan = {len(NAME_LIST)}")
    lines.append(f"# nvalues = 0")
    lines.append("# units = specified")
    for i, name in enumerate(NAME_LIST):
        lines.append(f"# name {i} = {name}")
    for i, (vmin, vmax) in enumerate(zip(SPAN_MIN, SPAN_MAX)):
        # Preserve formatting similar to sample
        if i in (7, 16):
            vmin_s = f"{vmin:.4e}"
            vmax_s = f"{vmax:.4e}"
        elif i in (11, 13):
            vmin_s = f"{int(vmin):10d}".strip()
            vmax_s = f"{int(vmax):10d}".strip()
        else:
            # choose 4 or 6 or 3 decimals depending on column
            if i in (2,):
                vmin_s = f"{vmin:8.3f}".strip()
                vmax_s = f"{vmax:8.3f}".strip()
            elif i in (1, 4):
                vmin_s = f"{vmin:.6f}"
                vmax_s = f"{vmax:.6f}"
            else:
                vmin_s = f"{vmin:.4f}"
                vmax_s = f"{vmax:.4f}"
        lines.append(f"# span {i} = {vmin_s:>12}, {vmax_s:>12}")

    lines.append(f"# interval = seconds: {interval_sec}")
    lines.append(f"# start_time = {start_time_line} [System UTC, first data scan.]")
    lines.append(f"# bad_flag = {BAD_FLAG}")

    # Sensors block is copied as comments for realism (static text)
    # Note: This is not parsed or used by the code; it is present to make the
    # output closely resemble files created by Seasave/datcnv.
    sensors_block = """
# <Sensors count="13" >
#   <sensor Channel="1" >
#     <!-- Frequency 0, Temperature -->
#     <TemperatureSensor SensorID="55" >
#       <SerialNumber>5932</SerialNumber>
#       <CalibrationDate>05-May-2023</CalibrationDate>
#       <UseG_J>1</UseG_J>
#       <A>0.00000000e+000</A>
#       <B>0.00000000e+000</B>
#       <C>0.00000000e+000</C>
#       <D>0.00000000e+000</D>
#       <F0_Old>0.000</F0_Old>
#       <G>4.33535100e-003</G>
#       <H>6.37964800e-004</H>
#       <I>2.23321700e-005</I>
#       <J>2.13213400e-006</J>
#       <F0>1000.000</F0>
#       <Slope>1.00000000</Slope>
#       <Offset>0.0000</Offset>
#     </TemperatureSensor>
#   </sensor>
#   <sensor Channel="2" >
#     <!-- Frequency 1, Conductivity -->
#     <ConductivitySensor SensorID="3" >
#       <SerialNumber>3168</SerialNumber>
#       <CalibrationDate>03-Apr-23</CalibrationDate>
#       <UseG_J>1</UseG_J>
#       <!-- Cell const and series R are applicable only for wide range sensors. -->
#       <SeriesR>0.0000</SeriesR>
#       <CellConst>2000.0000</CellConst>
#       <ConductivityType>0</ConductivityType>
#       <Coefficients equation="0" >
#         <A>0.00000000e+000</A>
#         <B>0.00000000e+000</B>
#         <C>0.00000000e+000</C>
#         <D>0.00000000e+000</D>
#         <M>0.0</M>
#         <CPcor>-9.57000000e-008</CPcor>
#       </Coefficients>
#       <Coefficients equation="1" >
#         <G>-9.81200100e+000</G>
#         <H>1.31345700e+000</H>
#         <I>-2.03661600e-003</I>
#         <J>2.07965100e-004</J>
#         <CPcor>-9.57000000e-008</CPcor>
#         <CTcor>3.2500e-006</CTcor>
#         <!-- WBOTC not applicable unless ConductivityType = 1. -->
#         <WBOTC>0.00000000e+000</WBOTC>
#       </Coefficients>
#       <Slope>1.00000000</Slope>
#       <Offset>0.00000</Offset>
#     </ConductivitySensor>
#   </sensor>
#   <sensor Channel="3" >
#     <!-- Frequency 2, Pressure, Digiquartz with TC -->
#     <PressureSensor SensorID="45" >
#       <SerialNumber>CTD22-#1039</SerialNumber>
#       <CalibrationDate>24-Jul-20223</CalibrationDate>
#       <C1>-5.037500e+004</C1>
#       <C2>1.287604e+000</C2>
#       <C3>1.563520e-002</C3>
#       <D1>3.537600e-002</D1>
#       <D2>0.000000e+000</D2>
#       <T1>2.982468e+001</T1>
#       <T2>1.134390e-004</T2>
#       <T3>3.966880e-006</T3>
#       <T4>3.342740e-009</T4>
#       <Slope>1.00000000</Slope>
#       <Offset>-0.61950</Offset>
#       <T5>0.000000e+000</T5>
#       <AD590M>1.281700e-002</AD590M>
#       <AD590B>-9.178660e+000</AD590B>
#     </PressureSensor>
#   </sensor>
#   <sensor Channel="4" >
#     <!-- Frequency 3, Temperature, 2 -->
#     <TemperatureSensor SensorID="55" >
#       <SerialNumber>6180</SerialNumber>
#       <CalibrationDate>05-May-2023</CalibrationDate>
#       <UseG_J>1</UseG_J>
#       <A>0.00000000e+000</A>
#       <B>0.00000000e+000</B>
#       <C>0.00000000e+000</C>
#       <D>0.00000000e+000</D>
#       <F0_Old>0.000</F0_Old>
#       <G>4.33716900e-003</G>
#       <H>6.34770400e-004</H>
#       <I>2.18641200e-005</I>
#       <J>2.02199700e-006</J>
#       <F0>1000.000</F0>
#       <Slope>1.00000000</Slope>
#       <Offset>0.0000</Offset>
#     </TemperatureSensor>
#   </sensor>
#   <sensor Channel="5" >
#     <!-- Frequency 4, Conductivity, 2 -->
#     <ConductivitySensor SensorID="3" >
#       <SerialNumber>4685</SerialNumber>
#       <CalibrationDate>03-Apr-23</CalibrationDate>
#       <UseG_J>1</UseG_J>
#       <!-- Cell const and series R are applicable only for wide range sensors. -->
#       <SeriesR>0.0000</SeriesR>
#       <CellConst>2000.0000</CellConst>
#       <ConductivityType>0</ConductivityType>
#       <Coefficients equation="0" >
#         <A>0.00000000e+000</A>
#         <B>0.00000000e+000</B>
#         <C>0.00000000e+000</C>
#         <D>0.00000000e+000</D>
#         <M>0.0</M>
#         <CPcor>-9.57000000e-008</CPcor>
#       </Coefficients>
#       <Coefficients equation="1" >
#         <G>-1.00331700e+001</G>
#         <H>1.35122700e+000</H>
#         <I>-1.98925600e-004</I>
#         <J>6.53698500e-005</J>
#         <CPcor>-9.57000000e-008</CPcor>
#         <CTcor>3.2500e-006</CTcor>
#         <!-- WBOTC not applicable unless ConductivityType = 1. -->
#         <WBOTC>0.00000000e+000</WBOTC>
#       </Coefficients>
#       <Slope>1.00000000</Slope>
#       <Offset>0.00000</Offset>
#     </ConductivitySensor>
#   </sensor>
#   <sensor Channel="6" >
#     <!-- A/D voltage 0, Oxygen, SBE 43 -->
#     <OxygenSensor SensorID="38" >
#       <SerialNumber>3159</SerialNumber>
#       <CalibrationDate>02-May-2023</CalibrationDate>
#       <Use2007Equation>1</Use2007Equation>
#       <CalibrationCoefficients equation="0" >
#         <!-- Coefficients for Owens-Millard equation. -->
#         <Boc>0.0000</Boc>
#         <Soc>0.0000e+000</Soc>
#         <offset>0.0000</offset>
#         <Pcor>0.00e+000</Pcor>
#         <Tcor>0.0000</Tcor>
#         <Tau>0.0</Tau>
#       </CalibrationCoefficients>
#       <CalibrationCoefficients equation="1" >
#         <!-- Coefficients for Sea-Bird equation - SBE calibration in 2007 and later. -->
#         <Soc>4.5613e-001</Soc>
#         <offset>-0.4999</offset>
#         <A>-4.0202e-003</A>
#         <B> 1.8188e-004</B>
#         <C>-2.6056e-006</C>
#         <D0> 2.5826e+000</D0>
#         <D1> 1.92634e-004</D1>
#         <D2>-4.64803e-002</D2>
#         <E> 3.6000e-002</E>
#         <Tau20> 1.0900</Tau20>
#         <H1>-3.3000e-002</H1>
#         <H2> 5.0000e+003</H2>
#         <H3> 1.4500e+003</H3>
#       </CalibrationCoefficients>
#     </OxygenSensor>
#   </sensor>
#   <sensor Channel="7" >
#     <!-- A/D voltage 1, Oxygen, SBE 43, 2 -->
#     <OxygenSensor SensorID="38" >
#       <SerialNumber>3199</SerialNumber>
#       <CalibrationDate>24-May-2023</CalibrationDate>
#       <Use2007Equation>1</Use2007Equation>
#       <CalibrationCoefficients equation="0" >
#         <!-- Coefficients for Owens-Millard equation. -->
#         <Boc>0.0000</Boc>
#         <Soc>0.0000e+000</Soc>
#         <offset>0.0000</offset>
#         <Pcor>0.00e+000</Pcor>
#         <Tcor>0.0000</Tcor>
#         <Tau>0.0</Tau>
#       </CalibrationCoefficients>
#       <CalibrationCoefficients equation="1" >
#         <!-- Coefficients for Sea-Bird equation - SBE calibration in 2007 and later. -->
#         <Soc>5.2417e-001</Soc>
#         <offset>-0.4591</offset>
#         <A>-5.1767e-003</A>
#         <B> 1.8250e-004</B>
#         <C>-2.5573e-006</C>
#         <D0> 2.5826e+000</D0>
#         <D1> 1.92634e-004</D1>
#         <D2>-4.64803e-002</D2>
#         <E> 3.6000e-002</E>
#         <Tau20> 0.9000</Tau20>
#         <H1>-3.3000e-002</H1>
#         <H2> 5.0000e+003</H2>
#         <H3> 1.4500e+003</H3>
#       </CalibrationCoefficients>
#     </OxygenSensor>
#   </sensor>
#   <sensor Channel="8" >
#     <!-- A/D voltage 2, PAR/Irradiance, Biospherical/Licor -->
#     <PAR_BiosphericalLicorChelseaSensor SensorID="42" >
#       <SerialNumber>70677</SerialNumber>
#       <CalibrationDate>26-Jul-2022</CalibrationDate>
#       <M>1.00000000</M>
#       <B>0.00000000</B>
#       <CalibrationConstant>18621973929.23650000</CalibrationConstant>
#       <ConversionUnits>1</ConversionUnits>
#       <Multiplier>1.00000000</Multiplier>
#       <Offset>-0.05412206</Offset>
#     </PAR_BiosphericalLicorChelseaSensor>
#   </sensor>
#   <sensor Channel="9" >
#     <!-- A/D voltage 3, Transmissometer, WET Labs C-Star -->
#     <WET_LabsCStar SensorID="71" >
#       <SerialNumber>CST-2009DR</SerialNumber>
#       <CalibrationDate>01-Dec-2021</CalibrationDate>
#       <M>21.3083</M>
#       <B>-0.1065</B>
#       <PathLength>0.250</PathLength>
#     </WET_LabsCStar>
#   </sensor>
#   <sensor Channel="10" >
#     <!-- A/D voltage 4, Free -->
#   </sensor>
#   <sensor Channel="11" >
#     <!-- A/D voltage 5, Free -->
#   </sensor>
#   <sensor Channel="12" >
#     <!-- A/D voltage 6, Free -->
#   </sensor>
#   <sensor Channel="13" >
#     <!-- A/D voltage 7, Free -->
#   </sensor>
# </Sensors>
# datcnv_date = {dt} , 7.26.7.129 [datcnv_vars = 16]
# datcnv_in = D:\\triaxus_processing\\in2023_v06\\seasave\\in2023_v06_07\\in2023_v06_07_XXX.hex D:\\triaxus_processing\\in2023_v06\\seasave\\in2023_v06_07\\in2023_v06_07_XXX.XMLCON
# datcnv_skipover = 0
# datcnv_ox_hysteresis_correction = yes
# datcnv_ox_tau_correction = yes
# file_type = ascii
""".strip("\n").format(dt=datetime.now().strftime("%b %d %Y %H:%M:%S"))
    lines.extend(sensors_block.splitlines())

    lines.append("*END*")
    return "\n".join(lines) + "\n"


def _fmt_row(values: List[float]) -> str:
    """Format one data row using spacing similar to sample CNV output."""
    (
        t0,
        c0,
        pr,
        t1,
        c1,
        o0,
        o1,
        par,
        cstar,
        sal0,
        sal1,
        scan,
        times,
        pumps,
        lat,
        lon,
        flag,
    ) = values

    parts = [
        f"{t0:10.4f}",
        f"{c0:10.6f}",
        f"{pr:10.3f}",
        f"{t1:10.4f}",
        f"{c1:10.6f}",
        f"{o0:10.3f}",
        f"{o1:10.3f}",
        f"{par:10.4e}",
        f"{cstar:10.4f}",
        f"{sal0:10.4f}",
        f"{sal1:10.4f}",
        f"{int(scan):10d}",
        f"{times:10.3f}",
        f"{int(pumps):10d}",
        f"{lat:10.5f}",
        f"{lon:10.5f}",
        f"{flag:10.3e}",
    ]
    return " ".join(parts) + "\n"


class RandomWalk:
    """Small helper for bounded random-walk value generation.

    Each call to ``step`` nudges a value by a Gaussian delta and reflects
    against the provided [vmin, vmax] bounds to stay within range.
    """

    def __init__(self, seed: Optional[int] = None):
        self._rng = random.Random(seed)

    def step(self, value: float, vmin: float, vmax: float, sigma: float) -> float:
        """Advance ``value`` by a Gaussian step and keep it within bounds."""
        delta = self._rng.gauss(0.0, sigma)
        newv = value + delta
        if newv < vmin:
            newv = vmin + (vmin - newv)
        if newv > vmax:
            newv = vmax - (newv - vmax)
        return max(vmin, min(vmax, newv))

    def choose_par_floor(self) -> float:
        """Occasionally force PAR to its low floor, mimicking night readings."""
        return 1.0e-12 if self._rng.random() < 0.1 else None  # 10% chance


def _row_to_obj(row: List[float]) -> dict:
    """Convert a numeric row list to a dict keyed by variable names."""
    obj = {}
    for i, key in enumerate(VAR_KEYS):
        obj[key] = row[i]
    return obj


def _read_last_lat_lon(path: str) -> Tuple[Optional[float], Optional[float]]:
    """Read the last data line from a CNV and extract lat/lon if present.

    Returns (lat, lon) or (None, None) if not found or parse error.
    """
    last_line = ""
    try:
        with open(path, "r") as rf:
            for line in rf:
                if line.strip() and not line.startswith("*") and not line.startswith("#"):
                    last_line = line
        if last_line:
            cols = last_line.split()
            if len(cols) >= 16:
                lat = float(cols[14])
                lon = float(cols[15])
                return lat, lon
    except Exception:
        pass
    return None, None


class MissionTrack:
    """Straight-line mission track between two lat/lon points.

    - Advances position at constant speed along the line from (start_lat, start_lon)
      to (end_lat, end_lon).
    - If ``pingpong`` is True, bounces at the ends; otherwise clamps at the end.
    - Speed is specified in knots for user friendliness; internal uses m/s.
    - Uses a simple local-plane approximation suitable for small mission spans.
    """

    KNOT_TO_MPS = 0.514444

    def __init__(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        speed_knots: float = 4.0,
        pingpong: bool = False,
    ):
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.end_lat = end_lat
        self.end_lon = end_lon
        self.speed_mps = max(0.0, float(speed_knots)) * self.KNOT_TO_MPS
        self.pingpong = bool(pingpong)

        # Precompute track geometry
        self._dlat_deg = self.end_lat - self.start_lat
        self._dlon_deg = self.end_lon - self.start_lon
        # Mid-lat for lon scaling
        self._mid_lat_rad = (self.start_lat + self.end_lat) / 2.0 * (3.141592653589793 / 180.0)
        m_per_deg_lat = 111320.0  # rough average
        m_per_deg_lon = 111320.0 * max(0.000001, abs(math.cos(self._mid_lat_rad)))
        dlat_m = self._dlat_deg * m_per_deg_lat
        dlon_m = self._dlon_deg * m_per_deg_lon
        self._length_m = (dlat_m ** 2 + dlon_m ** 2) ** 0.5
        # Degrees moved per meter along the track
        self._deg_lat_per_m = (self._dlat_deg / self._length_m) if self._length_m > 0 else 0.0
        self._deg_lon_per_m = (self._dlon_deg / self._length_m) if self._length_m > 0 else 0.0

        # Distance progressed from start along the line in meters and direction (1 or -1)
        self._s_m = 0.0
        self._dir = 1

    def reset_position(self, lat: float, lon: float):
        """Align the along-track distance to the provided lat/lon.

        Projects the vector (start->current) onto the track direction and
        clamps within [0, length].
        """
        if self._length_m <= 0:
            self._s_m = 0.0
            return
        # Work purely in degrees to find fraction, then scale by length_m
        dv_lat = lat - self.start_lat
        dv_lon = lon - self.start_lon
        denom = (self._dlat_deg ** 2 + self._dlon_deg ** 2)
        if denom <= 0:
            self._s_m = 0.0
            return
        t = (dv_lat * self._dlat_deg + dv_lon * self._dlon_deg) / denom
        t = max(0.0, min(1.0, t))
        self._s_m = t * self._length_m

    def step(self, dt: float) -> Tuple[float, float]:
        if self._length_m <= 0:
            # Degenerate: stay at end
            return self.end_lat, self.end_lon

        ds = self.speed_mps * max(0.0, dt) * self._dir
        self._s_m += ds
        if self.pingpong:
            # Reflect at ends
            if self._s_m > self._length_m:
                over = self._s_m - self._length_m
                self._s_m = self._length_m - over
                self._dir *= -1
            elif self._s_m < 0.0:
                self._s_m = -self._s_m
                self._dir *= -1
        else:
            # Clamp at ends
            if self._s_m > self._length_m:
                self._s_m = self._length_m
            if self._s_m < 0.0:
                self._s_m = 0.0

        lat = self.start_lat + self._deg_lat_per_m * self._s_m
        lon = self.start_lon + self._deg_lon_per_m * self._s_m
        return lat, lon


class CNVSimulator:
    """Continuously write simulated scans to a CNV file.

    - Creates a header when starting a new file.
    - Optionally appends to an existing file by resuming scan/time counters
      from the last data line.
    - Spawns a background thread that writes rows at ``interval`` seconds.
    """
    def __init__(
        self,
        out_path: str,
        interval: float = 0.0416667,
        seed: Optional[int] = None,
        append: bool = False,
        operator: str = "Ella",
        ship: str = "Investigator",
        cruise: str = "in2020_v09",
        station: str = "7",
        start_lat: float = -35.57462,
        start_lon: float = 154.30952,
        # Mission track options
        end_lat: Optional[float] = None,
        end_lon: Optional[float] = None,
        track_speed_knots: float = 6.0,
        track_pingpong: bool = True,
        on_row: Optional[Callable[[List[float]], None]] = None,
    ):
        self.out_path = out_path
        self.interval = interval
        self.operator = operator
        self.ship = ship
        self.cruise = cruise
        self.station = station
        self._rng = RandomWalk(seed)
        self._stop = threading.Event()
        self._run = threading.Event()
        self._lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._fh = None
        self._count_written = 0
        self._scan = 1
        self._time_s = 0.0
        self._pumps = 1
        self._lat = start_lat
        self._lon = start_lon
        self._track = None  # set below if end_lat/lon provided
        self._on_row = on_row

        # Initialize signal values at mid-spans for a stable starting point.
        self._t0 = (SPAN_MIN[0] + SPAN_MAX[0]) / 2
        self._c0 = (SPAN_MIN[1] + SPAN_MAX[1]) / 2
        self._pr = (SPAN_MIN[2] + SPAN_MAX[2]) / 2
        self._t1 = (SPAN_MIN[3] + SPAN_MAX[3]) / 2
        self._c1 = (SPAN_MIN[4] + SPAN_MAX[4]) / 2
        self._o0 = (SPAN_MIN[5] + SPAN_MAX[5]) / 2
        self._o1 = (SPAN_MIN[6] + SPAN_MAX[6]) / 2
        self._par = (SPAN_MIN[7] + SPAN_MAX[7]) / 2
        self._cstar = (SPAN_MIN[8] + SPAN_MAX[8]) / 2
        self._sal0 = (SPAN_MIN[9] + SPAN_MAX[9]) / 2
        self._sal1 = (SPAN_MIN[10] + SPAN_MAX[10]) / 2

        # Persist track defaults
        self._track_speed_knots = track_speed_knots
        self._track_pingpong = track_pingpong

        # Setup mission track if configured
        try:
            if end_lat is not None and end_lon is not None:
                self._track = MissionTrack(
                    start_lat=start_lat,
                    start_lon=start_lon,
                    end_lat=end_lat,
                    end_lon=end_lon,
                    speed_knots=self._track_speed_knots,
                    pingpong=self._track_pingpong,
                )
        except Exception:
            # If track setup fails for any reason, fall back to drift
            self._track = None

        if append and os.path.exists(out_path):
            self._open_for_append()
        else:
            self._start_new_file()

    # --- File management ---
    def _start_new_file(self):
        """Create a new CNV file and write a fresh header."""
        os.makedirs(os.path.dirname(self.out_path) or ".", exist_ok=True)
        header = _format_header(
            file_hex_path=self.out_path.replace(".cnv", ".hex"),
            operator=self.operator,
            ship=self.ship,
            cruise=self.cruise,
            station=self.station,
            start_lat=self._lat,
            start_lon=self._lon,
            interval_sec=self.interval,
        )
        with open(self.out_path, "w", newline="\n") as f:
            f.write(header)
        self._fh = open(self.out_path, "a", buffering=1)
        self._count_written = 0
        self._scan = 1
        self._time_s = 0.0

    def _open_for_append(self):
        """Open an existing CNV file and resume counters from the last row.

        This scans the file for the last non-header, non-empty line, parses the
        numeric columns, then updates internal counters and signal seeds so
        appended data continues smoothly.
        """
        self._fh = open(self.out_path, "r+", buffering=1)
        self._fh.seek(0, os.SEEK_END)
        # Find the last actual data line (skip header lines starting with * or #).
        last_line = ""
        with open(self.out_path, "r") as rf:
            for line in rf:
                if line.strip() and not line.startswith("*") and not line.startswith("#"):
                    last_line = line
        if last_line:
            try:
                cols = last_line.split()
                self._scan = int(cols[11]) + 1
                self._time_s = float(cols[12]) + self.interval
                self._pumps = int(cols[13])
                self._lat = float(cols[14])
                self._lon = float(cols[15])
                # Update internal signals from last row where feasible so the
                # random walk continues from previous values.
                self._t0 = float(cols[0])
                self._c0 = float(cols[1])
                self._pr = float(cols[2])
                self._t1 = float(cols[3])
                self._c1 = float(cols[4])
                self._o0 = float(cols[5])
                self._o1 = float(cols[6])
                self._par = float(cols[7])
                self._cstar = float(cols[8])
                self._sal0 = float(cols[9])
                self._sal1 = float(cols[10])
                # Align track position with last known lat/lon if a track is active
                if self._track is not None:
                    try:
                        self._track.reset_position(self._lat, self._lon)
                    except Exception:
                        pass
            except Exception:
                # If parsing fails, fall back to safe defaults (fresh counters).
                self._scan = 1
                self._time_s = 0.0
        else:
            # No data found: ensure a proper header exists by recreating file.
            self._fh.close()
            self._start_new_file()

        # reopen in append mode
        if not self._fh.closed:
            self._fh.close()
        self._fh = open(self.out_path, "a", buffering=1)

    # --- Control ---
    def start(self):
        """Start or resume the background writer thread."""
        if self._thread and self._thread.is_alive():
            self._run.set()
            return
        self._stop.clear()
        self._run.set()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def pause(self):
        """Temporarily pause writing without stopping the thread."""
        self._run.clear()

    def resume(self):
        """Resume writing after a pause."""
        self._run.set()

    def stop(self):
        """Stop the background thread and close the file handle."""
        self._run.clear()
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        if self._fh:
            self._fh.flush()
            self._fh.close()
    
    def set_on_row(self, cb: Optional[Callable[[List[float]], None]]):
        """Register or clear a live row callback."""
        self._on_row = cb

    def switch_to_new_file(self, new_path: str):
        """Close current file and start a brand new CNV at ``new_path``."""
        with self._lock:
            if self._fh:
                self._fh.flush()
                self._fh.close()
            self.out_path = new_path
            self._start_new_file()

    def switch_to_append_file(self, path: str):
        """Close current file and append to an existing CNV at ``path``."""
        with self._lock:
            if self._fh:
                self._fh.flush()
                self._fh.close()
            self.out_path = path
            self._open_for_append()

    def clear_current_file(self):
        """Delete the current CNV file and start a fresh one with a new header.

        Safe to call while running; acquires internal lock and resets counters.
        """
        # Pause writer so we don't race file operations
        self._run.clear()
        with self._lock:
            if self._fh:
                try:
                    self._fh.flush()
                except Exception:
                    pass
                try:
                    self._fh.close()
                except Exception:
                    pass
            try:
                if os.path.exists(self.out_path):
                    os.remove(self.out_path)
            except Exception:
                # If deletion fails, proceed to truncate via _start_new_file
                pass
            self._start_new_file()
        # Keep paused; caller can resume explicitly (route picker does this on new route)

    def update_track(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float,
                     speed_knots: Optional[float] = None, pingpong: Optional[bool] = None):
        """Atomically update the mission track. If simulator is running, takes effect immediately.

        If ``speed_knots`` or ``pingpong`` are None, keep previous values.
        """
        with self._lock:
            if speed_knots is not None:
                self._track_speed_knots = float(speed_knots)
            if pingpong is not None:
                self._track_pingpong = bool(pingpong)
            # Immediately move current position to provided start
            self._lat = start_lat
            self._lon = start_lon
            self._track = MissionTrack(
                start_lat=start_lat,
                start_lon=start_lon,
                end_lat=end_lat,
                end_lon=end_lon,
                speed_knots=self._track_speed_knots,
                pingpong=self._track_pingpong,
            )

    def set_track_speed(self, speed_knots: float):
        with self._lock:
            try:
                self._track_speed_knots = float(speed_knots)
            except Exception:
                return
            if self._track is not None:
                self._track.speed_mps = self._track_speed_knots * MissionTrack.KNOT_TO_MPS

    def status(self) -> str:
        """Return a short human-readable summary of current state."""
        return (
            f"file={self.out_path} scans={self._scan-1} timeS={self._time_s:.3f} "
            f"lat={self._lat:.5f} lon={self._lon:.5f} running={self._run.is_set()}"
        )

    # --- Writing loop ---
    def _loop(self):
        """Writer loop running in a background thread.

        Uses a simple tick scheduler based on ``time.perf_counter`` to target
        the configured output rate. When paused, it sleeps briefly and resets
        the next tick to avoid catching up too quickly on resume.
        """
        next_tick = time.perf_counter()
        while not self._stop.is_set():
            if not self._run.is_set():
                time.sleep(0.05)
                next_tick = time.perf_counter() + self.interval
                continue

            now = time.perf_counter()
            if now < next_tick:
                time.sleep(min(0.005, next_tick - now))
                continue
            next_tick += self.interval

            with self._lock:
                row = self._next_row()
                self._fh.write(_fmt_row(row))
                self._count_written += 1
                if self._on_row is not None:
                    try:
                        self._on_row(row)
                    except Exception:
                        pass

    # --- Data generation ---
    def _next_row(self) -> List[float]:
        """Generate the next scan values using bounded random walks.

        Step sizes are tuned for smoothness. PAR occasionally snaps to a very
        low "floor" to mimic night-time readings.
        """
        # Signal step sizes (tune for smoothness)
        self._t0 = self._rng.step(self._t0, SPAN_MIN[0], SPAN_MAX[0], 0.003)
        self._c0 = self._rng.step(self._c0, SPAN_MIN[1], SPAN_MAX[1], 0.0002)
        self._pr = self._rng.step(self._pr, SPAN_MIN[2], SPAN_MAX[2], 0.15)
        self._t1 = self._rng.step(self._t1, SPAN_MIN[3], SPAN_MAX[3], 0.003)
        self._c1 = self._rng.step(self._c1, SPAN_MIN[4], SPAN_MAX[4], 0.0002)
        self._o0 = self._rng.step(self._o0, SPAN_MIN[5], SPAN_MAX[5], 0.20)
        self._o1 = self._rng.step(self._o1, SPAN_MIN[6], SPAN_MAX[6], 0.20)

        par_floor = self._rng.choose_par_floor()
        if par_floor is None:
            self._par = self._rng.step(self._par, SPAN_MIN[7], SPAN_MAX[7], (SPAN_MAX[7]-SPAN_MIN[7]) * 0.05)
        else:
            self._par = par_floor

        self._cstar = self._rng.step(self._cstar, SPAN_MIN[8], SPAN_MAX[8], 0.10)
        self._sal0 = self._rng.step(self._sal0, SPAN_MIN[9], SPAN_MAX[9], 0.001)
        self._sal1 = self._rng.step(self._sal1, SPAN_MIN[10], SPAN_MAX[10], 0.001)

        # Latitude/longitude: follow mission track if set, else drift slowly.
        if self._track is not None:
            self._lat, self._lon = self._track.step(self.interval)
        else:
            self._lat = self._rng.step(self._lat, SPAN_MIN[14], SPAN_MAX[14], 0.00005)
            self._lon = self._rng.step(self._lon, SPAN_MIN[15], SPAN_MAX[15], 0.00005)

        # Pump is constant (1), flag is always 0; increment time/scan counters.
        row = [
            self._t0,
            self._c0,
            self._pr,
            self._t1,
            self._c1,
            self._o0,
            self._o1,
            self._par,
            self._cstar,
            self._sal0,
            self._sal1,
            float(self._scan),
            round(self._time_s, 3),
            float(self._pumps),
            self._lat,
            self._lon,
            0.0,
        ]
        self._scan += 1
        self._time_s += self.interval
        return row


def interactive_cli(default_path: str, autostart: bool = True, **sim_kwargs):
    """Simple REPL to control the simulator during manual runs.

    Commands:
      - start/new/append <path>: choose file and mode
      - pause/resume: control writing without stopping
      - status: show current counters and file path
      - rate <hz>: change output rate on the fly
      - stop/quit: exit the simulator
    """
    print("CNV live-feed simulator. Commands: start <path>|append <path>|new <path>, pause, resume, status, rate <hz>, stop/quit")
    sim: Optional[CNVSimulator] = None
    if autostart:
        sim = CNVSimulator(default_path, append=False, **sim_kwargs)
        sim.start()
        # If route picker server is active, expose a reroute callback bound to this sim
        if globals().get("_ROUTE_LIVE_STATE") is not None:
            def _reroute(sel: dict):
                s_lat = float(sel.get("start_lat", sim._lat))
                s_lon = float(sel.get("start_lon", sim._lon))
                e_lat = float(sel.get("end_lat", sim._lat))
                e_lon = float(sel.get("end_lon", sim._lon))
                spd = sel.get("speed_knots")
                sim.update_track(s_lat, s_lon, e_lat, e_lon, speed_knots=spd)
            globals()["_ROUTE_REROUTE_CB"] = _reroute
            def _control(action: str):
                if action == "pause":
                    sim.pause()
                elif action == "resume":
                    sim.resume()
                elif action == "clear":
                    sim.clear_current_file()
                    st = globals().get("_ROUTE_LIVE_STATE")
                    if st:
                        try:
                            with st["lock"]:
                                st["rows"].clear()
                        except Exception:
                            pass
            globals()["_ROUTE_CONTROL_CB"] = _control
            globals()["_ROUTE_SET_SPEED_CB"] = lambda val: sim.set_track_speed(val)
        print(f"Auto-started. Writing to: {default_path}")
    while True:
        try:
            cmd = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            cmd = "quit"

        if not cmd:
            continue

        toks = cmd.split()
        op = toks[0].lower()
        arg = toks[1] if len(toks) > 1 else None

        if op in ("quit", "exit", "q", "stop"):
            if sim:
                sim.stop()
            print("bye")
            return
        elif op == "start":
            path = arg or default_path
            if sim:
                sim.stop()
            sim = CNVSimulator(path, append=False, **sim_kwargs)
            sim.start()
            if globals().get("_ROUTE_LIVE_STATE") is not None:
                def _reroute(sel: dict):
                    s_lat = float(sel.get("start_lat", sim._lat))
                    s_lon = float(sel.get("start_lon", sim._lon))
                    e_lat = float(sel.get("end_lat", sim._lat))
                    e_lon = float(sel.get("end_lon", sim._lon))
                    spd = sel.get("speed_knots")
                    sim.update_track(s_lat, s_lon, e_lat, e_lon, speed_knots=spd)
                globals()["_ROUTE_REROUTE_CB"] = _reroute
                def _control(action: str):
                    if action == "pause":
                        sim.pause()
                    elif action == "resume":
                        sim.resume()
                    elif action == "clear":
                        sim.clear_current_file()
                        st = globals().get("_ROUTE_LIVE_STATE")
                        if st:
                            try:
                                with st["lock"]:
                                    st["rows"].clear()
                            except Exception:
                                pass
                globals()["_ROUTE_CONTROL_CB"] = _control
                globals()["_ROUTE_SET_SPEED_CB"] = lambda val: sim.set_track_speed(val)
            print(f"Started new file: {path}")
        elif op == "new":
            path = arg or default_path
            if not sim:
                sim = CNVSimulator(path, append=False, **sim_kwargs)
            else:
                sim.switch_to_new_file(path)
            sim.start()
            if globals().get("_ROUTE_LIVE_STATE") is not None:
                def _reroute(sel: dict):
                    s_lat = float(sel.get("start_lat", sim._lat))
                    s_lon = float(sel.get("start_lon", sim._lon))
                    e_lat = float(sel.get("end_lat", sim._lat))
                    e_lon = float(sel.get("end_lon", sim._lon))
                    spd = sel.get("speed_knots")
                    sim.update_track(s_lat, s_lon, e_lat, e_lon, speed_knots=spd)
                globals()["_ROUTE_REROUTE_CB"] = _reroute
                def _control(action: str):
                    if action == "pause":
                        sim.pause()
                    elif action == "resume":
                        sim.resume()
                    elif action == "clear":
                        sim.clear_current_file()
                        st = globals().get("_ROUTE_LIVE_STATE")
                        if st:
                            try:
                                with st["lock"]:
                                    st["rows"].clear()
                            except Exception:
                                pass
                globals()["_ROUTE_CONTROL_CB"] = _control
                globals()["_ROUTE_SET_SPEED_CB"] = lambda val: sim.set_track_speed(val)
            print(f"Switched to new file: {path}")
        elif op == "append":
            path = arg or default_path
            if not os.path.exists(path):
                print(f"No such file to append: {path}")
                continue
            if not sim:
                sim = CNVSimulator(path, append=True, **sim_kwargs)
            else:
                sim.switch_to_append_file(path)
            sim.start()
            if globals().get("_ROUTE_LIVE_STATE") is not None:
                def _reroute(sel: dict):
                    s_lat = float(sel.get("start_lat", sim._lat))
                    s_lon = float(sel.get("start_lon", sim._lon))
                    e_lat = float(sel.get("end_lat", sim._lat))
                    e_lon = float(sel.get("end_lon", sim._lon))
                    sim.update_track(s_lat, s_lon, e_lat, e_lon)
                globals()["_ROUTE_REROUTE_CB"] = _reroute
                def _control(action: str):
                    if action == "pause":
                        sim.pause()
                    elif action == "resume":
                        sim.resume()
                    elif action == "clear":
                        sim.clear_current_file()
                globals()["_ROUTE_CONTROL_CB"] = _control
            print(f"Appending to existing: {path}")
        elif op == "pause":
            if sim:
                sim.pause()
                print("paused")
            else:
                print("not running")
        elif op in ("resume", "continue"):
            if sim:
                sim.resume()
                print("resumed")
            else:
                print("not running")
        elif op == "status":
            if sim:
                print(sim.status())
            else:
                print("no simulator yet")
        elif op == "rate":
            if not sim:
                print("start a simulator first")
                continue
            if not arg:
                print(f"current rate: {1.0/sim.interval:.3f} Hz")
            else:
                try:
                    hz = float(arg)
                    if hz <= 0:
                        raise ValueError
                    sim.interval = 1.0 / hz
                    print(f"rate set to {hz:.3f} Hz")
                except ValueError:
                    print("usage: rate <hz>")
        else:
            print("commands: start <path> | append <path> | new <path> | pause | resume | status | rate <hz> | quit")


def main():
    """Parse CLI args and run in interactive or non-interactive mode."""
    parser = argparse.ArgumentParser(description="Simulate TRIAXUS writing a .cnv live-feed file")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, "triaxus_sim_001.cnv")
    parser.add_argument("--file", dest="file", default=default_path)
    parser.add_argument("--hz", dest="hz", type=float, default=24.0, help="Output rate in Hz (default 24Hz)")
    parser.add_argument("--seed", dest="seed", type=int, default=None, help="Random seed for reproducibility")
    # Mission track options
    parser.add_argument("--start-lat", type=float, default=-35.57462, help="Mission start latitude [deg]")
    parser.add_argument("--start-lon", type=float, default=154.30952, help="Mission start longitude [deg]")
    parser.add_argument("--start-city", type=str, default=None, help="Mission start city name (overrides --start-lat/--start-lon if known)")
    parser.add_argument("--end-lat", type=float, default=None, help="Mission end latitude [deg]; enable track when set with --end-lon")
    parser.add_argument("--end-lon", type=float, default=None, help="Mission end longitude [deg]; enable track when set with --end-lat")
    parser.add_argument("--end-city", type=str, default=None, help="Mission end city name (enables track; overrides --end-lat/--end-lon if known)")
    parser.add_argument("--speed-knots", type=float, default=6.0, help="Track speed in knots (default 6.0) when mission track enabled")
    # Default pingpong ON; allow disabling with --no-pingpong
    parser.add_argument("--pingpong", dest="pingpong", action="store_true", default=True, help="Bounce back and forth on the mission track (default ON)")
    parser.add_argument("--no-pingpong", dest="pingpong", action="store_false", help="Do not bounce; stop at the end of the mission track")
    parser.add_argument("--append", action="store_true", help="Append to existing file instead of starting a new one")
    parser.add_argument("--noninteractive", action="store_true", help="Run non-interactively for --count scans")
    parser.add_argument("--count", type=int, default=0, help="When --noninteractive, how many scans to write (0=forever)")
    # Route picker (opens a local map to choose start/end then continues)
    parser.add_argument("--route-picker", action="store_true", help="Open a browser map to select start/end and use them")
    # Live display
    parser.add_argument("--live", action="store_true", help="Print periodic live row summaries to stdout")
    parser.add_argument("--live-every", type=int, default=24, help="Print every N rows when --live is set (default 24)")
    parser.add_argument(
        "--live-fields",
        type=str,
        default="scan,timeS,latitude,longitude,prDM,t090C,sal00",
        help="Comma list of fields to print when --live is set",
    )
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.file) or ".", exist_ok=True)

    # Resolve city names to coordinates if provided (lat/lon flags take precedence if also set explicitly)
    start_lat = args.start_lat
    start_lon = args.start_lon
    if args.start_city:
        key = args.start_city.strip().lower()
        if key in CITY_COORDS:
            start_lat, start_lon = CITY_COORDS[key]
        else:
            print(f"[warn] Unknown start city: {args.start_city}. Using --start-lat/--start-lon.", file=sys.stderr)

    end_lat = args.end_lat
    end_lon = args.end_lon
    if args.end_city:
        key = args.end_city.strip().lower()
        if key in CITY_COORDS:
            end_lat, end_lon = CITY_COORDS[key]
        else:
            print(f"[warn] Unknown end city: {args.end_city}. Use --end-lat/--end-lon to specify.", file=sys.stderr)
    # If requested, open a local route picker and wait for selection.
    if args.route_picker:
        selected = _run_route_picker_and_wait(args.file)
        if selected is not None:
            start_lat = selected.get("start_lat", start_lat)
            start_lon = selected.get("start_lon", start_lon)
            end_lat = selected.get("end_lat", end_lat)
            end_lon = selected.get("end_lon", end_lon)
            print(f"[route] start=({start_lat:.5f},{start_lon:.5f}) end=({end_lat:.5f},{end_lon:.5f})")
        else:
            print("[route] No selection received; continuing with existing coordinates.")

    # Setup live on_row callback composition
    def _compose_callbacks(*cbs):
        def _cb(row):
            for f in cbs:
                if f:
                    try:
                        f(row)
                    except Exception:
                        pass
        return _cb

    live_cb = None
    if args.live:
        fields = [s.strip() for s in args.live_fields.split(",") if s.strip()]
        # Create LivePrinter instance
        class LivePrinter:
            """Prints a compact summary of selected fields every N rows."""
            def __init__(self, every: int = 24, fields: Optional[List[str]] = None):
                self.every = max(1, int(every))
                self._n = 0
                default = ["scan", "timeS", "latitude", "longitude", "prDM", "t090C", "sal00"]
                fields = fields or default
                indices = []
                labels = []
                for f in fields:
                    key = f.strip()
                    if not key:
                        continue
                    idx = VAR_INDEX_LC.get(key.lower())
                    if idx is not None:
                        indices.append(idx)
                        labels.append(VAR_KEYS[idx])
                self._indices = indices
                self._labels = labels

            def __call__(self, row: List[float]):
                self._n += 1
                if (self._n % self.every) != 0:
                    return
                parts = []
                for label, idx in zip(self._labels, self._indices):
                    val = row[idx]
                    if label in ("latitude", "longitude"):
                        parts.append(f"{label}={val:.5f}")
                    elif label in ("timeS",):
                        parts.append(f"{label}={val:.3f}")
                    elif label in ("scan", "pumps"):
                        parts.append(f"{label}={int(val)}")
                    elif label in ("prDM",):
                        parts.append(f"{label}={val:.2f}")
                    elif label in ("t090C", "t190C", "sal00", "sal11", "CStarTr0"):
                        parts.append(f"{label}={val:.3f}")
                    else:
                        parts.append(f"{label}={val}")
                try:
                    print("live:", ", ".join(parts), flush=True)
                except Exception:
                    pass
        live_cb = LivePrinter(every=args.live_every, fields=fields)
    route_cb = None
    if args.route_picker:
        def route_cb(row):
            st = globals().get("_ROUTE_LIVE_STATE")
            if not st:
                return
            try:
                with st["lock"]:
                    st["rows"].append(row)
            except Exception:
                pass

    on_row_cb = _compose_callbacks(live_cb, route_cb)

    if args.noninteractive:
        # Headless mode: run until Ctrl+C or until --count scans are written.
        sim = CNVSimulator(
            args.file,
            interval=1.0/args.hz,
            seed=args.seed,
            append=args.append,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            track_speed_knots=args.speed_knots,
            track_pingpong=args.pingpong,
            on_row=on_row_cb,
        )
        sim.start()
        # Expose reroute callback for route picker page
        if args.route_picker:
            def _reroute(sel: dict):
                # Use provided start; if not present, fall back to current position
                s_lat = float(sel.get("start_lat", sim._lat))
                s_lon = float(sel.get("start_lon", sim._lon))
                e_lat = float(sel.get("end_lat", sim._lat))
                e_lon = float(sel.get("end_lon", sim._lon))
                sim.update_track(s_lat, s_lon, e_lat, e_lon)
            globals()["_ROUTE_REROUTE_CB"] = _reroute
            def _control(action: str):
                if action == "pause":
                    sim.pause()
                elif action == "resume":
                    sim.resume()
            globals()["_ROUTE_CONTROL_CB"] = _control
        try:
            if args.count <= 0:
                while True:
                    time.sleep(1)
            else:
                # Sleep in short intervals until enough scans are written.
                target_scan = args.count
                while sim._scan - 1 < target_scan:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            sim.stop()
    else:
        # If stdin is not interactive (e.g., launched by a non-TTY tool),
        # keep generating until Ctrl+C instead of quitting on EOF.
        if not sys.stdin.isatty():
            sim = CNVSimulator(
                args.file,
                interval=1.0/args.hz,
                seed=args.seed,
                append=args.append,
                start_lat=start_lat,
                start_lon=start_lon,
                end_lat=end_lat,
                end_lon=end_lon,
                track_speed_knots=args.speed_knots,
                track_pingpong=args.pingpong,
                on_row=on_row_cb,
            )
            sim.start()
            if args.route_picker:
                def _reroute(sel: dict):
                    s_lat = float(sel.get("start_lat", sim._lat))
                    s_lon = float(sel.get("start_lon", sim._lon))
                    e_lat = float(sel.get("end_lat", sim._lat))
                    e_lon = float(sel.get("end_lon", sim._lon))
                    spd = sel.get("speed_knots")
                    sim.update_track(s_lat, s_lon, e_lat, e_lon, speed_knots=spd)
                globals()["_ROUTE_REROUTE_CB"] = _reroute
                def _control(action: str):
                    if action == "pause":
                        sim.pause()
                    elif action == "resume":
                        sim.resume()
                    # Non-interactive/TTY path does not expose clear here
                globals()["_ROUTE_CONTROL_CB"] = _control
                globals()["_ROUTE_SET_SPEED_CB"] = lambda val: sim.set_track_speed(val)
            print(f"Non-interactive stdin detected. Writing to: {args.file}. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                sim.stop()
        else:
            # Interactive terminal: start immediately and run until stop/quit.
            try:
                # Start interactive CLI directly (autostarted). Reroute/control callbacks
                # are bound inside interactive_cli when route picker server is active.
                interactive_cli(
                    args.file,
                    autostart=True,
                    start_lat=start_lat,
                    start_lon=start_lon,
                    end_lat=end_lat,
                    end_lon=end_lon,
                    track_speed_knots=args.speed_knots,
                    track_pingpong=args.pingpong,
                    on_row=on_row_cb,
                )
            except KeyboardInterrupt:
                # Graceful shutdown on Ctrl+C
                print("\nInterrupted. Exiting.")


if __name__ == "__main__":
    main()
