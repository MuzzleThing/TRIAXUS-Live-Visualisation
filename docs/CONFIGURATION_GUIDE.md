## TRIAXUS Configuration & Deployment Guide

This guide describes a clean, reproducible setup for TRIAXUS on macOS and Linux, including Python, PostgreSQL, configuration with Dynaconf, optional Mapbox, and test verification.

### 1) Prerequisites
- Git
- Python 3.9–3.12 recommended
- pip and virtualenv (or `python -m venv`)
- PostgreSQL 13+ (for database features)

### 2) Clone the repository
```bash
git clone <your-fork-or-repo-url>
cd TRIAXUS visualisation project/triaxus-plotter
```

### 3) Python environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) PostgreSQL installation

#### macOS (Homebrew)
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 5) Database initialization
Create dedicated user, database, and schema using the provided SQL script.

```bash
# login as postgres superuser
sudo -u postgres psql  # Linux
# or: psql postgres     # if your user has access

-- inside psql
CREATE ROLE triaxus_user WITH LOGIN PASSWORD 'your_password';
CREATE DATABASE triaxus_db OWNER triaxus_user;
GRANT ALL PRIVILEGES ON DATABASE triaxus_db TO triaxus_user;
\q

# apply schema
psql "postgresql://triaxus_user:your_password@localhost:5432/triaxus_db" \
  -f triaxus/database/sql/init_database.sql
```

Notes:
- All identifiers (table/column names) are lowercase for PostgreSQL compatibility.
- Re-running the SQL file is idempotent for existing objects in most cases; handle drops separately if needed.

### 6) Configuration with Dynaconf
TRIAXUS reads configuration from `configs/default.yaml` and optional overrides in `configs/custom.yaml`. Configure this AFTER the database is created and reachable.

Recommended patterns (separate guidance for testing/development vs production):

- Single `custom.yaml` with environments:
```yaml
# configs/custom.yaml

# Development & Testing (can be plaintext in file)
default:
  theme: "oceanographic"
  DATABASE:
    enabled: true
    url: "postgresql://triaxus_user:dev_password@localhost:5432/triaxus_db"

testing:
  DATABASE:
    enabled: true
    url: "postgresql://triaxus_user:test_password@localhost:5432/triaxus_db_test"

# Production (no plaintext secrets in files)
production:
  DATABASE:
    enabled: true
    url: "${DATABASE_URL}"
  MAPBOX:
    token: "${MAPBOX_TOKEN}"
```

#### Testing/Development
- You may keep throwaway credentials directly in `configs/custom.yaml` for convenience.
- Recommended DB URL examples are shown above.
- In CI you can still use env vars, but plaintext in a private CI secret file is acceptable for test-only data.

#### Production
- Do not store any passwords/tokens in files or images.
- Set required values via environment variables only (examples below).
- Typical sources: Docker/Kubernetes secrets, systemd drop-in with `Environment=`, CI secret stores.

- Select the active environment (defaults to development):
```bash
export ENV_FOR_DYNACONF=production   # or testing / production
```

Environment variables (set differently for test/dev vs production):
```bash
# Common
export DB_ENABLED=true

# Testing/Development example
export ENV_FOR_DYNACONF=testing
export DATABASE_URL="postgresql://triaxus_user:test_password@localhost:5432/triaxus_db_test"

# Production example (env-only)
export ENV_FOR_DYNACONF=production
export DATABASE_URL="postgresql://triaxus_user:STRONG_SECRET@db-host:5432/triaxus_db"
export MAPBOX_TOKEN="your_mapbox_token"
```

Notes:
- Environment variables always take precedence over file values (e.g., `DATABASE_URL` overrides `DATABASE.url`).
- Use a separate PostgreSQL database for testing (e.g., `triaxus_db_test`).
- Production: never commit real passwords/tokens; rely on environment variables or secret stores.

### 7) Quick verification
Run the quick test runner (DB connectivity + basic plotting):
```bash
source .venv/bin/activate
python tests/test_runner_quick.py
```

Run the comprehensive end-to-end test:
```bash
python tests/test_comprehensive.py
```

Run the unified test runner:
```bash
python tests/test_runner.py
```

### 8) CLI usage sanity check
```bash
python triaxus-plot time-series --variables tv290c,sal00 --output ts_demo.html
python triaxus-plot map --map-style open-street-map --output map_demo.html
```

### 9) Optional: Mapbox configuration
Mapbox enables high-quality online map tiles.

- Set token via env:
```bash
export MAPBOX_TOKEN="your_token_here"
```

- Or in `configs/custom.yaml`:
```yaml
MAPBOX:
  token: "your_token_here"
```

Without a token, the system uses offline/OSM fallbacks automatically.

### 10) Directory layout (key paths)
```
configs/
  default.yaml           # shipped defaults
  custom.yaml            # your overrides (optional)
triaxus/database/sql/
  init_database.sql      # schema creation
tests/
  test_runner.py         # full suite
  test_runner_quick.py   # fast checks
  test_comprehensive.py  # end-to-end
docs/
  CONFIGURATION_GUIDE.md
  TESTING.md
```

 

### 11) Troubleshooting

- PostgreSQL fails to start
  - macOS: `brew services restart postgresql@14`
  - Linux: `sudo systemctl status postgresql && sudo journalctl -u postgresql -n 100`

- Cannot connect to DB
  - Verify env: `echo $DATABASE_URL` and `echo $DB_ENABLED`
  - Test psql:
    ```bash
    psql "${DATABASE_URL}" -c "SELECT 1;"
    ```
  - Check firewall or listen address in `postgresql.conf` if remote.

- Schema/column mismatch
  - Re-apply `triaxus/database/sql/init_database.sql`
  - Confirm models use lowercase columns and that your DB matches.

- Map tiles not showing
  - Ensure `MAPBOX_TOKEN` is set for Mapbox styles
  - Otherwise use `--map-style open-street-map`

- Long-running tests
  - Use `tests/test_runner_quick.py` during development
  - If a hang occurs, check for circular dependencies (already resolved in current codebase) and re-run with `-v` to inspect logs.

### 12) Production considerations
- Use a dedicated PostgreSQL instance with regular backups
- Set strong credentials via environment variables
- Consider connection pooling parameters in SQLAlchemy engine (configured via settings)
- Serve generated HTML through a static file server (nginx, S3 + CDN, etc.)

### 13) Uninstall / clean up
```bash
deactivate
rm -rf .venv

# Optional: drop DB (careful!)
psql -U postgres -c "DROP DATABASE IF EXISTS triaxus_db;"
psql -U postgres -c "DROP ROLE IF EXISTS triaxus_user;"
```

---
If you need an infrastructure-as-code variant (Docker or Ansible), we can add a companion setup in a future iteration.


