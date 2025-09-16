# TRIAXUS CNV Live-Feed Simulator

## Quick Start

- Run interactively (default 24 Hz) and start writing to `triaxus_sim_001.cnv` in this folder:
  - `python3 simulation.py`
- Stop with `Ctrl+C` or type `stop`/`quit` in the prompt.

## Requirements

- Python 3.8+
- No external dependencies

## CLI Options

- `--file <path>`: Output CNV path (default: `./triaxus_sim_001.cnv`).
- `--hz <float>`: Output rate in Hz (default: `24.0`).
- `--seed <int>`: Seed the RNG for reproducible values.
- `--append`: Append to an existing file instead of starting new.
- `--noninteractive`: Run headless (use with `--count` or stop via `Ctrl+C`).
- `--count <int>`: In `--noninteractive` mode, write this many scans (0=forever).

## Interactive Commands

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

## Non-Interactive Examples

- Run at 10 Hz until interrupted:
  - `python simulation.py --hz 10 --noninteractive`
- Write exactly 5,000 scans at 24 Hz, then exit:
  - `python simulation.py --count 5000 --noninteractive`
- Append to an existing file, continuing counters:
  - `python simulation.py --append --noninteractive --file ./existing.cnv`

## Output Format

- Header: Starts with `*` and `#` lines (Seasave-style metadata, variable names, spans).
- Data rows: Whitespace-separated columns matching the header variable list. Key columns include temperatures, conductivity, pressure, oxygen, PAR, transmissometer, salinity, scan count, elapsed seconds, pumps, latitude, longitude, and a flag.

The generator keeps values within realistic spans using a bounded random walk; PAR occasionally snaps to a low floor to mimic nighttime readings. Latitude/longitude drift slowly within configured bounds.

## Notes

- Default output path is alongside `simulation.py` as `triaxus_sim_001.cnv`.
- Changing `--hz` updates the interval to `1 / hz`.
- Use `--seed` for deterministic streams when testing.
