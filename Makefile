# TRIAXUS Live Visualization Makefile

.PHONY: help install install-dev setup-db init-db migrate upgrade downgrade test lint format clean docker-build docker-up docker-down logs

# Default target
help:
	@echo "TRIAXUS Live Visualization - Available commands:"
	@echo ""
	@echo "Development Setup:"
	@echo "  install         Install production dependencies"
	@echo "  install-dev     Install development dependencies"
	@echo "  setup-db        Setup database (create + migrate)"
	@echo "  init-db         Initialize database with extensions and tables"
	@echo ""
	@echo "Database Management:"
	@echo "  migrate         Create new migration"
	@echo "  upgrade         Apply pending migrations"
	@echo "  downgrade       Rollback last migration"
	@echo ""
	@echo "Code Quality:"
	@echo "  test            Run tests"
	@echo "  test-cov        Run tests with coverage report"
	@echo "  lint            Run linting checks"
	@echo "  format          Format code with black and isort"
	@echo "  mypy            Run type checking"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build    Build Docker images"
	@echo "  docker-up       Start all services"
	@echo "  docker-up-dev   Start with development profile"
	@echo "  docker-down     Stop all services"
	@echo "  docker-logs     View logs"
	@echo ""
	@echo "Utilities:"
	@echo "  clean           Clean temporary files"
	@echo "  backup-db       Backup database"

# Installation
install:
	uv sync --frozen --no-dev

install-dev:
	uv sync --frozen

# Database setup
setup-db: init-db upgrade

init-db:
	python triaxus_backend/scripts/init_db.py

migrate:
	cd triaxus_backend && alembic revision --autogenerate -m "$(MSG)"

upgrade:
	cd triaxus_backend && alembic upgrade head

downgrade:
	cd triaxus_backend && alembic downgrade -1

# Testing
test:
	pytest triaxus_backend/tests/

test-cov:
	pytest triaxus_backend/tests/ --cov=triaxus_backend --cov-report=html --cov-report=term

test-integration:
	pytest triaxus_backend/tests/integration/ -v

# Code quality
lint:
	flake8 triaxus_backend/
	black --check triaxus_backend/
	isort --check-only triaxus_backend/

format:
	black triaxus_backend/
	isort triaxus_backend/

mypy:
	mypy triaxus_backend/

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-up-dev:
	docker-compose --profile development up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-logs-backend:
	docker-compose logs -f backend

docker-restart:
	docker-compose restart

# Database backup
backup-db:
	docker-compose exec database pg_dump -U triaxus_user triaxus_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Monitoring and maintenance
monitor:
	docker-compose exec backend python -m triaxus_backend.scripts.monitor_system

clean-cache:
	docker-compose exec redis redis-cli FLUSHALL

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Development server
dev-server:
	uvicorn triaxus_backend.main:app --reload --host 0.0.0.0 --port 8000

# Celery workers (for development)
dev-worker:
	celery -A triaxus_backend.tasks.celery_app worker --loglevel=info

dev-beat:
	celery -A triaxus_backend.tasks.celery_app beat --loglevel=info

# Monitor celery
celery-monitor:
	celery -A triaxus_backend.tasks.celery_app flower