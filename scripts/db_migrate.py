#!/usr/bin/env python3
"""
Simple Alembic-based migration runner for TRIAXUS (PostgreSQL only).

Provides commands to upgrade/downgrade, show history/current, and create
new revisions (optionally with autogenerate). It resolves the database URL
from `DATABASE_URL` or SecureDatabaseConfigManager.
"""

import os
import sys
import argparse
from pathlib import Path

from alembic import command
from alembic.config import Config


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_config() -> Config:
    root = _project_root()
    alembic_ini = root / "db_migrations" / "alembic.ini"
    cfg = Config(str(alembic_ini))

    # Ensure script location resolves relative to project root
    cfg.set_main_option("script_location", str(root / "db_migrations"))

    # Prefer DATABASE_URL env var; otherwise try SecureDatabaseConfigManager
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            sys.path.insert(0, str(root))
            from triaxus.database.config_manager import SecureDatabaseConfigManager  # type: ignore

            url = SecureDatabaseConfigManager().get_connection_url()
        except Exception:
            url = "postgresql://user:password@localhost:5432/triaxus_db"

    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def main() -> None:
    parser = argparse.ArgumentParser(description="TRIAXUS DB Migration Runner (PostgreSQL)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_up = sub.add_parser("upgrade", help="Upgrade database to a target revision (default: head)")
    p_up.add_argument("target", nargs="?", default="head")

    p_down = sub.add_parser("downgrade", help="Downgrade database to a target revision (e.g., -1)")
    p_down.add_argument("target")

    sub.add_parser("current", help="Show current revision")
    sub.add_parser("history", help="Show migration history")

    p_rev = sub.add_parser("revision", help="Create a new revision")
    p_rev.add_argument("-m", "--message", required=True)
    p_rev.add_argument("--autogenerate", action="store_true", help="Autogenerate from models metadata")

    p_stamp = sub.add_parser("stamp", help="Stamp the database with a specific revision (no migration)")
    p_stamp.add_argument("revision", help="Revision id, e.g., head or 0001_initial_baseline")

    args = parser.parse_args()
    cfg = _load_config()

    if args.cmd == "upgrade":
        command.upgrade(cfg, args.target)
    elif args.cmd == "downgrade":
        command.downgrade(cfg, args.target)
    elif args.cmd == "current":
        command.current(cfg)
    elif args.cmd == "history":
        command.history(cfg)
    elif args.cmd == "revision":
        command.revision(cfg, message=args.message, autogenerate=args.autogenerate)
    elif args.cmd == "stamp":
        command.stamp(cfg, args.revision)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

