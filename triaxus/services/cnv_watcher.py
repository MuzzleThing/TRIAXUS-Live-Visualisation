#!/usr/bin/env python3
"""
Cross-platform CNV watcher daemon wrapper.

This utility starts/stops a detached background process that runs:
  python -m triaxus.data.cnv_processor --watch

It manages a pidfile and simple status reporting. No external dependencies.
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path


PIDFILE_DEFAULT = Path(".runtime/cnv_watcher.pid")
LOGFILE_DEFAULT = Path("logs/cnv_watcher.log")


def ensure_dirs():
    PIDFILE_DEFAULT.parent.mkdir(parents=True, exist_ok=True)
    LOGFILE_DEFAULT.parent.mkdir(parents=True, exist_ok=True)


def is_process_running(pid: int) -> bool:
    try:
        # On Unix, sending signal 0 checks existence without killing
        if os.name != "nt":
            os.kill(pid, 0)
            return True
        else:
            # On Windows, os.kill with signal.CTRL_BREAK_EVENT requires console.
            # Fallback: if process exists, killing with 0 is not supported.
            # We attempt to open a handle by sending no-op via tasklist.
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True)
            return str(pid) in out.stdout
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but different privileges
        return True


def read_pid(pidfile: Path) -> int:
    try:
        content = pidfile.read_text(encoding="utf-8").strip()
        return int(content)
    except Exception:
        return -1


def write_pid(pidfile: Path, pid: int) -> None:
    pidfile.write_text(str(pid), encoding="utf-8")


def start(pidfile: Path = PIDFILE_DEFAULT, logfile: Path = LOGFILE_DEFAULT, extra_args: list[str] | None = None) -> int:
    ensure_dirs()
    if pidfile.exists():
        pid = read_pid(pidfile)
        if pid > 0 and is_process_running(pid):
            print(f"CNV watcher already running (pid {pid})")
            return 0
        else:
            # stale pidfile
            pidfile.unlink(missing_ok=True)

    cmd = [sys.executable, "-m", "triaxus.data.cnv_processor", "--watch"]
    if extra_args:
        cmd.extend(extra_args)

    stdout = open(logfile, "a", buffering=1, encoding="utf-8")
    stderr = stdout

    creationflags = 0
    preexec_fn = None
    if os.name == "nt":
        # CREATE_NEW_PROCESS_GROUP (0x00000200) | DETACHED_PROCESS (0x00000008)
        creationflags = 0x00000200 | 0x00000008
    else:
        # Start new session to detach from controlling terminal
        preexec_fn = os.setsid

    proc = subprocess.Popen(
        cmd,
        stdout=stdout,
        stderr=stderr,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
        preexec_fn=preexec_fn,
        close_fds=True,
        cwd=str(Path.cwd()),
    )

    write_pid(pidfile, proc.pid)
    print(f"CNV watcher started (pid {proc.pid}), logging to {logfile}")
    return 0


def stop(pidfile: Path = PIDFILE_DEFAULT, timeout: float = 10.0) -> int:
    if not pidfile.exists():
        print("CNV watcher not running (no pidfile)")
        return 0

    pid = read_pid(pidfile)
    if pid <= 0:
        pidfile.unlink(missing_ok=True)
        print("Stale pidfile removed")
        return 0

    if not is_process_running(pid):
        pidfile.unlink(missing_ok=True)
        print("CNV watcher not running (stale pidfile removed)")
        return 0

    try:
        if os.name == "nt":
            # Attempt graceful termination
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False)
        else:
            os.kill(pid, signal.SIGTERM)
    except Exception as e:
        print(f"Failed to signal process {pid}: {e}")

    # Wait for exit
    start_t = time.time()
    while time.time() - start_t < timeout:
        if not is_process_running(pid):
            pidfile.unlink(missing_ok=True)
            print("CNV watcher stopped")
            return 0
        time.sleep(0.2)

    print("CNV watcher did not exit in time")
    return 1


def status(pidfile: Path = PIDFILE_DEFAULT) -> int:
    if not pidfile.exists():
        print("CNV watcher status: stopped")
        return 3
    pid = read_pid(pidfile)
    if pid > 0 and is_process_running(pid):
        print(f"CNV watcher status: running (pid {pid})")
        return 0
    else:
        print("CNV watcher status: stale pidfile; removing")
        pidfile.unlink(missing_ok=True)
        return 3


def parse_args(argv: list[str]) -> tuple[str, list[str]]:
    # Very lightweight parser to keep module self-contained
    action = argv[1] if len(argv) > 1 else "status"
    extra = []
    # Allow passing through extra args to watch (e.g., --no-plot in future)
    if len(argv) > 2:
        extra = argv[2:]
    return action, extra


if __name__ == "__main__":
    ensure_dirs()
    action, extra = parse_args(sys.argv)
    if action in ("start", "--start"):
        sys.exit(start(extra_args=extra))
    elif action in ("stop", "--stop"):
        sys.exit(stop())
    elif action in ("status", "--status"):
        sys.exit(status())
    else:
        print("Usage: python -m triaxus.services.cnv_watcher [start|stop|status] [extra watch args]")
        print("Example: python -m triaxus.services.cnv_watcher start")
        sys.exit(2)


