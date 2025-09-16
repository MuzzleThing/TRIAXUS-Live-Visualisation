# TRIAXUS CNV Live‑Feed Simulator

This simulator produces a live `.cnv` file that looks like a Sea‑Bird CTD data stream. The easiest way to drive it is the Route Picker map (primary mode). A CLI is available as an alternative.

## Primary Mode: Route Picker (Map UI)

Launch the simulator with the map UI:

- `python3 live_data_feed_simulation/simulation.py --route-picker`

What you’ll see and do:

- If your CNV already has rows with lat/lon, START is pre‑filled from the latest row; otherwise pick START then END on the map.
- Set Speed (kn): defaults to `5000` in the UI. This value is applied when you click “Start in Simulator”.
- Click “Start in Simulator”:
  - The simulator starts writing immediately (ship starts at your selected START).
  - Selection is locked — you can pan/zoom but not pick new points until you reset.
- Live features:
  - Solid green polyline = actual track being written.
  - Orange (START → ship) and blue dashed (ship → END) show the planned route already walked vs to walk.
  - Live Data panel (right) shows the latest values (scan/time/lat/lon/temp/sal/pressure).
  - “Follow Ship” toggles auto‑pan.
  - “Pause” / “Resume” control the writer.
  - “Clear File” deletes and recreates the CNV with a fresh header, clears live buffers, removes markers/lines, turns off Follow, and unlocks selection so you can pick a new START/END and click “Start in Simulator” again.

Notes

- While running, clicks on the map only pan/zoom (no point selection) until you click “Clear File”.
- “Start in Simulator” resumes writing automatically (no need to press Resume).
- When you re‑pick a route, the ship always starts from your selected START.

## Requirements

- Python 3.8+
- No external dependencies

## CLI (optional)

You can run without the map using CLI flags. The route picker is recommended for most use‑cases; CLI remains useful for scripting and headless runs.

CLI options:

- `--file <path>`: Output CNV path (default: `./triaxus_sim_001.cnv`).
- `--hz <float>`: Output rate in Hz (default: `24.0`).
- `--seed <int>`: Seed the RNG for reproducible values.
- `--append`: Append to an existing file instead of starting new.
- `--noninteractive`: Run headless (use with `--count` or stop via `Ctrl+C`).
- `--count <int>`: In `--noninteractive` mode, write this many scans (0=forever).
- `--start-lat <deg>` / `--start-lon <deg>`: Mission start coordinates (defaults to `-35.57462`, `154.30952`).
- `--start-city <name>`: Use a known city/port name for start (overrides start lat/lon if known; small offline list).
- `--end-lat <deg>` / `--end-lon <deg>`: Mission end coordinates. When both are provided, latitude/longitude follow a straight mission track.
- `--end-city <name>`: Use a known city/port name for end (enables track; overrides end lat/lon if known).
- `--speed-knots <float>`: Track speed in knots when mission track is enabled (CLI default `6.0`). The map UI defaults to `5000`.
- `--pingpong` / `--no-pingpong`: Ping-pong defaults ON; use `--no-pingpong` to stop at end.
- `--route-picker`: Open a browser map, click START and END, then the simulator uses those coordinates automatically.
- `--live` (with `--live-every`, `--live-fields`): Print periodic live row summaries to stdout.

## Interactive Commands (REPL)

When started interactively you get a small REPL:

- `start <path>` / `new <path>` / `append <path>`: select file and mode
- `pause` / `resume`: control writing without stopping
- `status`: show current counters and file path
- `rate <hz>`: change output rate on the fly
- `stop` / `quit`: exit the simulator

Example session:

```
$ python simulation.py
CNV live-feed simulator. Commands: start <path>|append <path>|new <path>, pause, resume, status, rate <hz>, stop/quit
> status
file=./triaxus_sim_001.cnv scans=120 timeS=5.000 lat=-35.57462 lon=154.30952 running=True
> rate 10
rate set to 10.000 Hz
> stop
bye
```

## Non‑Interactive Examples (headless)

- Run at 10 Hz until interrupted:
  - `python simulation.py --hz 10 --noninteractive`
- Write exactly 5,000 scans at 24 Hz, then exit:
  - `python simulation.py --count 5000 --noninteractive`
- Append to an existing file, continuing counters:
  - `python simulation.py --append --noninteractive --file ./existing.cnv`
- Follow a mission track from start to end at 5 knots:
  - `python simulation.py --start-lat -35.60 --start-lon 154.30 --end-lat -35.20 --end-lon 154.33 --speed-knots 5 --noninteractive`
- Ping-pong along a line between two points at 3 knots:
  - `python simulation.py --start-lat -35.50 --start-lon 154.31 --end-lat -35.25 --end-lon 154.32 --speed-knots 3 --pingpong --noninteractive`
- Start/end by city names (offline lookup):
  - `python simulation.py --start-city Sydney --end-city Hobart --noninteractive`

## Map UI (manual open)

- You can also open the map directly at `Live_data_feed_simulation/offline/route_picker.html`.
- When opened manually, “Start in Simulator” only works if the simulator is running with `--route-picker` (so the local server is up).

## Output Format

- Header: Starts with `*` and `#` lines (Seasave-style metadata, variable names, spans).
- Data rows: Whitespace-separated columns matching the header variable list. Key columns include temperatures, conductivity, pressure, oxygen, PAR, transmissometer, salinity, scan count, elapsed seconds, pumps, latitude, longitude, and a flag.

The generator keeps values within realistic spans using a bounded random walk; PAR occasionally snaps to a low floor to mimic nighttime readings. In route mode, latitude/longitude follow the mission track.

## Notes

- Default output path is alongside `simulation.py` as `triaxus_sim_001.cnv`.
- Fresh runs overwrite by default; use `--append` to continue writing to an existing file.
- “Clear File” fully resets the current `.cnv` (new header) and the live state; the next “Start in Simulator” immediately resumes writing.
- Changing `--hz` updates the interval to `1 / hz`.
- Use `--seed` for deterministic streams when testing.
