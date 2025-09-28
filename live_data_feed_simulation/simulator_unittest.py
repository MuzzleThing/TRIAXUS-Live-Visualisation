import os
import re
import time
import tempfile
import importlib.util
import unittest

# -------- import the simulator from the same folder --------
HERE = os.path.abspath(os.path.dirname(__file__))
SIM_PATH = os.path.join(HERE, "simulation.py")
spec = importlib.util.spec_from_file_location("simulation", SIM_PATH)
simulation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(simulation)

# ----------------- helpers -----------------
def _read_header_data(path):
    header, data = [], []
    with open(path, "r") as f:
        for line in f:
            if line.startswith(("*", "#")):
                header.append(line.rstrip("\n"))
            elif line.strip():
                data.append(line.rstrip("\n"))
    return header, data

def _count_data_rows(path):
    try:
        with open(path, "r") as f:
            return sum(1 for ln in f if ln.strip() and not ln.startswith(("*", "#")))
    except FileNotFoundError:
        return 0

def _get_nquan(header_lines):
    for hl in header_lines:
        m = re.match(r"#\s*nquan\s*=\s*(\d+)", hl.strip())
        if m:
            return int(m.group(1))
    return None

def _parse_cols(line):
    parts = line.split()
    # indices based on simulator output format:
    #  12th = scan (index 11), 13th = timeS (12), 15th = lat (14), 16th = lon (15)
    scan = int(float(parts[11]))
    timeS = float(parts[12])
    lat = float(parts[14])
    lon = float(parts[15])
    return scan, timeS, lat, lon, len(parts)

def _run_sim_and_wait(out_path, *, target_rows=80, interval=1/60.0,
                      start_lat=-31.95, start_lon=115.86,
                      end_lat=-32.06, end_lon=115.74,
                      speed_knots=6.0, pingpong=True, timeout_s=20):
    sim = simulation.CNVSimulator(
        out_path=out_path,
        interval=interval,
        seed=123,
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon,
        track_speed_knots=speed_knots,
        track_pingpong=pingpong,
    )
    sim.start()
    deadline = time.time() + timeout_s
    while time.time() < deadline and _count_data_rows(out_path) < target_rows:
        time.sleep(0.02)
    sim.stop()
    # let any buffers flush
    time.sleep(0.1)

# ================== one short run used by 3 tests ==================
class TestCNVBasic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = tempfile.TemporaryDirectory()
        cls.out = os.path.join(cls.td.name, "out_basic.cnv")
        # Faster interval so we don’t wait long; ~80 rows in a second+.
        _run_sim_and_wait(
            cls.out, target_rows=80, interval=1/60.0,
            start_lat=-31.95, start_lon=115.86,
            end_lat=-32.06, end_lon=115.74,
            speed_knots=6.0, pingpong=True, timeout_s=20
        )
        cls.header, cls.data = _read_header_data(cls.out)
        if not cls.data:
            raise RuntimeError("Simulator produced no data rows for basic test.")

    @classmethod
    def tearDownClass(cls):
        cls.td.cleanup()

    def test_header_has_nquan(self):
        nquan = _get_nquan(self.header)
        self.assertIsNotNone(nquan, "Missing '# nquan = <N>' in header")

    def test_first_row_column_count_and_numeric(self):
        nquan = _get_nquan(self.header)
        self.assertIsNotNone(nquan, "Missing '# nquan = <N>' in header")
        # column count match
        _, _, _, _, first_cols = _parse_cols(self.data[0])
        self.assertEqual(first_cols, nquan, f"First row has {first_cols} cols; expected {nquan}")
        # numeric tokens sanity
        tokens = self.data[0].split()
        numeric_like = 0
        for t in tokens:
            try:
                float(t.replace("e+", "e").replace("e-", "e-"))
                numeric_like += 1
            except Exception:
                pass
        self.assertGreaterEqual(numeric_like, nquan - 1, "Expected most tokens to be numeric")

    def test_scan_time_monotonic_and_bounds(self):
        scans, times, lats, lons = [], [], [], []
        for dl in self.data:
            s, t, la, lo, _ = _parse_cols(dl)
            scans.append(s); times.append(t); lats.append(la); lons.append(lo)
        self.assertTrue(all(b > a for a, b in zip(scans, scans[1:])), "scan should strictly increase")
        self.assertTrue(all(b >= a for a, b in zip(times, times[1:])), "timeS should be non-decreasing")
        self.assertTrue(all(-90.0 <= v <= 90.0 for v in lats), "latitude out of bounds")
        self.assertTrue(all(-180.0 <= v <= 180.0 for v in lons), "longitude out of bounds")

# ================== separate run to prove ping-pong ==================
class TestPingPongReversal(unittest.TestCase):
    def test_pingpong_reverses_direction(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "out_pp.cnv")
            # Very short track so we hit the endpoint and bounce quickly.
            # Over ~120 rows at 60 Hz we should see a reversal.
            _run_sim_and_wait(
                out,
                target_rows=160,
                interval=1/60.0,
                start_lat=-31.95000, start_lon=115.86000,
                end_lat=-31.95005, end_lon=115.86005,  # ~5e-5 deg separation
                speed_knots=6.0,
                pingpong=True,
                timeout_s=20,
            )
            _, data = _read_header_data(out)
            self.assertGreaterEqual(len(data), 120, "Not enough rows to detect reversal")

            # Compare early and late direction vectors
            def vec(pair_a, pair_b):
                (la1, lo1), (la2, lo2) = pair_a, pair_b
                return (la2 - la1, lo2 - lo1)

            # sample a few points from start and end to smooth noise
            def parse_latlon(line):
                parts = line.split()
                return float(parts[14]), float(parts[15])

            head_pts = [parse_latlon(data[i]) for i in range(0, min(5, len(data)))]
            tail_pts = [parse_latlon(data[-i]) for i in range(1, min(6, len(data)))]

            d_start = vec(head_pts[0], head_pts[-1])
            d_end   = vec(tail_pts[-1], tail_pts[0])  # chronological order

            dot = d_start[0]*d_end[0] + d_start[1]*d_end[1]
            self.assertLessEqual(dot, 0.0, "Expected direction reversal when pingpong=True")

if __name__ == "__main__":
    unittest.main(verbosity=2)
