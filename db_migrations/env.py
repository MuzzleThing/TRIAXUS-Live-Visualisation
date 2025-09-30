"""
Alembic migration environment for TRIAXUS (triaxus.database models).

This environment targets PostgreSQL and uses the SQLAlchemy Base metadata
from `triaxus.database.models` for autogeneration.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure project root is on sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import Base metadata from triaxus models
from triaxus.database.models import Base  # noqa: E402

# Optional: use SecureDatabaseConfigManager to resolve URL when env var not present
try:
    from triaxus.database.config_manager import SecureDatabaseConfigManager  # noqa: E402
except Exception:  # pragma: no cover
    SecureDatabaseConfigManager = None


# Alembic Config object
config = context.config

# Configure loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate'
target_metadata = Base.metadata


def get_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    if SecureDatabaseConfigManager is not None:
        try:
            mgr = SecureDatabaseConfigManager()
            return mgr.get_connection_url()
        except Exception:
            pass
    # Fallback
    return "postgresql://user:password@localhost:5432/triaxus_db"


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

