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

#### 7.1 Basic plotting tests
Run the modern test runner (pytest-based):
```bash
source .venv/bin/activate

# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --type unit
python tests/run_tests.py --type integration
python tests/run_tests.py --type e2e

# Run with verbose output
python tests/run_tests.py --verbose

# Run specific test patterns
python tests/run_tests.py --pattern database
python tests/run_tests.py --pattern plot

# Show test structure
python tests/run_tests.py --structure
```

#### 7.2 CLI usage sanity check
```bash
python triaxus-plot time-series --variables tv290c,sal00 --output ts_demo.html
python triaxus-plot map --map-style open-street-map --output map_demo.html
```

#### 7.3 Real-time system tests

**Start the complete real-time pipeline:**
```bash
# One-click start (recommended)
python scripts/start_realtime_pipeline.py
```

**Manual start (alternative):**
```bash
# Start data simulation
python live_data_feed_simulation/simulation.py \
  --file testdataQC/live_realtime_demo.cnv \
  --hz 1.0 \
  --live-every 5 \
  --start-city sydney \
  --end-city melbourne \
  --speed-knots 15 \
  --noninteractive &

# Start real-time processor
python -m triaxus.data.cnv_realtime_processor \
  --watch \
  --config configs/realtime_test.yaml \
  --verbose &

# Start API server
python realtime/realtime_api_server.py 8080 &
```

**Verify real-time components:**
```bash
# Check if processes are running
ps aux | grep -E "(simulation|cnv_realtime_processor|realtime_api_server)"

# Test API endpoint
curl http://localhost:8080/api/latest_data

# Check generated plots
ls -la tests/output/realtime_plots/
```

**Access the web dashboard:**
- Open http://localhost:8080 in your browser
- Verify plots are updating with real-time data
- Test different time granularities (5m, 15m, 30m, 1h, 6h, 12h, 24h, 3d, 7d, 30d, all)
- Test different refresh rates (0.5s, 1s, 2s, 5s, 10s, 30s, 1min, 5min, 10min, 15min, 30min, 1hour, manual)
- Default: 1 minute refresh, 1 hour time range

**Stop the real-time pipeline:**
```bash
# One-click stop (recommended)
python scripts/stop_realtime_pipeline.py

# Or manually stop processes
pkill -f simulation.py
pkill -f cnv_realtime_processor
pkill -f realtime_api_server
```

### 8) Optional: Mapbox configuration
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

### 9) Directory layout (key paths)
```
configs/
  default.yaml           # shipped defaults
  custom.yaml            # your overrides (optional)
  realtime_test.yaml     # real-time testing configuration
triaxus/database/sql/
  init_database.sql      # schema creation
tests/
  run_tests.py           # modern pytest-based test runner
  unit/                  # unit tests
  integration/           # integration tests
  e2e/                   # end-to-end tests
  output/realtime_plots/ # generated real-time plots
scripts/
  start_realtime_pipeline.py  # one-click real-time start
  stop_realtime_pipeline.py   # one-click real-time stop
realtime/
  realtime_api_server.py # API server for dashboard
  dashboard.html         # web dashboard
  dashboard.css          # dashboard styles
  dashboard.js           # dashboard JavaScript
live_data_feed_simulation/
  simulation.py          # CNV data simulator
docs/
  CONFIGURATION_GUIDE.md
  REALTIME_QUICK_START.md
  REALTIME_DATA_PROCESSING.md
  DATA_FLOW_DIAGRAM.md
```

 

### 10) Troubleshooting

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
  - Use `python tests/run_tests.py --type unit` during development
  - If a hang occurs, check for circular dependencies (already resolved in current codebase) and re-run with `-v` to inspect logs.

- Real-time pipeline issues
  - Check if all processes are running: `ps aux | grep -E "(simulation|cnv_realtime_processor|realtime_api_server)"`
  - Verify database connection: `curl http://localhost:8080/api/status`
  - Check generated plots: `ls -la tests/output/realtime_plots/`
  - Restart pipeline: `python scripts/stop_realtime_pipeline.py && python scripts/start_realtime_pipeline.py`
  - Check logs: `tail -f processor.log` or `tail -f processor_debug.log`

### 11) Production considerations
- Use a dedicated PostgreSQL instance with regular backups
- Set strong credentials via environment variables
- Consider connection pooling parameters in SQLAlchemy engine (configured via settings)
- Serve generated HTML through a static file server (nginx, S3 + CDN, etc.)

### 12) Uninstall / clean up
```bash
deactivate
rm -rf .venv

# Optional: drop DB (careful!)
psql -U postgres -c "DROP DATABASE IF EXISTS triaxus_db;"
psql -U postgres -c "DROP ROLE IF EXISTS triaxus_user;"
```

---
If you need an infrastructure-as-code variant (Docker or Ansible), we can add a companion setup in a future iteration.


### Data Validation Settings

The `data.validation` section in `configs/default.yaml` drives quality control for
all processors and plotters. Key fields include:

- `duplicate_subset` and `duplicate_threshold` for controlling acceptable levels of duplicated observations.
- `defaults.warn_missing_ratio` / `defaults.error_missing_ratio` to set baseline thresholds for missing data per column.
- `column_rules` to declare per-variable expectations (data type, bounds, and optional thresholds).
- `anomaly_detection` parameters (z-score threshold, minimum samples, warning/error ratios) for basic outlier detection.

These values can be overridden in `configs/custom.yaml` to tune validation for
different deployments.

### Archiving Settings

The new `archiving` block configures how processed datasets are stored:

- `directory`, `ensure_directory`, and `include_timestamp` control the destination for archived artefacts.
- `file_format` (currently `csv`) and `compress` toggle on-disk output.
- `write_quality_report` and `metadata_fields` determine whether JSON companions
  containing quality metrics and metadata are persisted.
- `store_in_database` enables database persistence via the existing ORM layer.

These settings are used by `triaxus.data.Archiver` to produce consistent, auditable
archives of processed TRIAXUS datasets.
