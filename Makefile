.PHONY: help install install-dev test lint format clean clean-data clean-all status ingest demo

help: ## Show this help message
	@echo "EIA Storage Accrual Engine - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	poetry install --only main

install-dev: ## Install all dependencies including development
	poetry install

test: ## Run tests with coverage
	poetry run pytest --cov=src/eia_sa --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without coverage
	poetry run pytest

lint: ## Run linting and type checking
	poetry run ruff check src/ tests/
	poetry run mypy src/
	poetry run black --check src/ tests/
	poetry run isort --check-only src/ tests/

format: ## Format code with black and isort
	poetry run black src/ tests/
	poetry run isort src/ tests/

clean: ## Clean Python cache and build files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

clean-data: ## Clean data directories (WARNING: removes all data)
	rm -rf data/bronze/*
	rm -rf data/silver/*
	rm -rf data/gold/*
	rm -rf outputs/*
	rm -rf logs/*

clean-all: clean clean-data ## Clean everything including data

status: ## Show system status
	poetry run python -m cli.app status

ingest: ## Ingest weekly storage data (2010-present)
	poetry run python -m cli.app ingest-weekly --start 2010-01-01

ingest-capacity: ## Ingest capacity data
	poetry run python -m cli.app ingest-capacity

build-silver: ## Build silver layer tables
	poetry run python -m cli.app build-silver

build-gold: ## Build gold layer tables (requires asof date)
	@echo "Usage: make build-gold ASOF=YYYY-MM-DD"
	@echo "Example: make build-gold ASOF=2025-08-31"
	@if [ -z "$(ASOF)" ]; then \
		echo "Error: ASOF parameter required"; \
		exit 1; \
	fi
	poetry run python -m cli.app build-gold --asof $(ASOF)

calc-accruals: ## Calculate accruals (requires asof date)
	@echo "Usage: make calc-accruals ASOF=YYYY-MM-DD"
	@echo "Example: make calc-accruals ASOF=2025-08-31"
	@if [ -z "$(ASOF)" ]; then \
		echo "Error: ASOF parameter required"; \
		exit 1; \
	fi
	poetry run python -m cli.app calc-accruals --asof $(ASOF)

dashboard: ## Launch Streamlit dashboard
	poetry run streamlit run dashboard/app.py

demo: ## Run complete demo workflow
	@echo "🚀 Running EIA Storage Accrual Engine Demo"
	@echo "=========================================="
	@echo ""
	@echo "1. Checking system status..."
	@make status
	@echo ""
	@echo "2. Ingesting weekly storage data..."
	@make ingest
	@echo ""
	@echo "3. Ingesting capacity data..."
	@make ingest-capacity
	@echo ""
	@echo "4. Building silver layer..."
	@make build-silver
	@echo ""
	@echo "5. Building gold layer..."
	@make build-gold ASOF=2025-08-31
	@echo ""
	@echo "6. Calculating accruals..."
	@make calc-accruals ASOF=2025-08-31
	@echo ""
	@echo "✅ Demo complete! Launch dashboard with: make dashboard"

setup-env: ## Set up environment file
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️  Please edit .env and add your EIA API key"; \
	else \
		echo "✅ .env file already exists"; \
	fi

pre-commit: ## Install pre-commit hooks
	poetry run pre-commit install

pre-commit-run: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

docker-build: ## Build Docker image
	docker build -t eia-storage-accrual .

docker-run: ## Run Docker container
	docker run -p 8501:8501 -v $(PWD)/data:/app/data eia-storage-accrual

deploy: ## Deploy to production (placeholder)
	@echo "🚀 Production deployment not yet implemented"
	@echo "💡 This would include:"
	@echo "   - Environment validation"
	@echo "   - Database migrations"
	@echo "   - Service deployment"
	@echo "   - Health checks"

# Development workflow shortcuts
dev-setup: install-dev setup-env pre-commit ## Complete development setup
	@echo "✅ Development environment ready!"
	@echo "💡 Next steps:"
	@echo "   1. Edit .env with your EIA API key"
	@echo "   2. Run: make demo"
	@echo "   3. Run: make dashboard"

quick-test: ## Quick development test
	@echo "🧪 Running quick development test..."
	@make lint
	@make test-fast
	@echo "✅ Quick test complete!"

# Git workflow
commit: ## Commit with conventional message (requires MESSAGE)
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Error: MESSAGE parameter required"; \
		echo "Usage: make commit MESSAGE='feat: add new feature'"; \
		exit 1; \
	fi
	git add -A
	git commit -m "$(MESSAGE)"

push: ## Push to remote repository
	git push origin main

# Documentation
docs-serve: ## Serve documentation locally
	@echo "📚 Documentation serving not yet implemented"
	@echo "💡 This would start a local docs server"

docs-build: ## Build documentation
	@echo "📚 Documentation building not yet implemented"
	@echo "💡 This would build HTML/PDF docs"

# Monitoring and maintenance
health-check: ## Run system health checks
	@echo "🏥 Running system health checks..."
	@make status
	@echo "✅ Health check complete!"

backup: ## Create backup of data and configuration
	@echo "💾 Creating backup..."
	@mkdir -p backups/$(shell date +%Y%m%d_%H%M%S)
	@cp -r data backups/$(shell date +%Y%m%d_%H%M%S)/data
	@cp .env backups/$(shell date +%Y%m%d_%H%M%S)/env
	@echo "✅ Backup created in backups/$(shell date +%Y%m%d_%H%M%S)"

restore: ## Restore from backup (requires BACKUP_DIR)
	@if [ -z "$(BACKUP_DIR)" ]; then \
		echo "Error: BACKUP_DIR parameter required"; \
		echo "Usage: make restore BACKUP_DIR=backups/20250101_120000"; \
		exit 1; \
	fi
	@echo "🔄 Restoring from backup: $(BACKUP_DIR)"
	@cp -r $(BACKUP_DIR)/data .
	@cp $(BACKUP_DIR)/env .env
	@echo "✅ Restore complete!"
