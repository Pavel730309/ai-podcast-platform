.PHONY: help install dev test lint build deploy clean setup-vps

# Default target
help:
	@echo "AI Podcast Platform - Available Commands:"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Start development environment"
	@echo "  make dev-local     - Start backend and frontend locally"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-coverage - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start production containers"
	@echo "  make down          - Stop containers"
	@echo "  make logs          - View logs"
	@echo ""
	@echo "🚀 Deployment:"
	@echo "  make setup-vps     - Setup fresh VPS (run as root)"
	@echo "  make deploy        - Deploy to production"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean         - Clean up containers and volumes"
	@echo "  make backup        - Create backup"
	@echo "  make update        - Update to latest version"

# Installation
install:
	@echo "📦 Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Development
dev:
	@echo "🚀 Starting development environment..."
	docker-compose -f backend/docker-compose.dev.yml up --build

dev-detached:
	docker-compose -f backend/docker-compose.dev.yml up --build -d

dev-local:
	@echo "🚀 Starting local development..."
	cd backend && uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev &
	@echo "Services started!"

# Testing
test:
	@echo "🧪 Running tests..."
	cd backend && pytest -v

test-coverage:
	cd backend && pytest --cov=app --cov-report=html --cov-report=term

# Linting
lint:
	@echo "🔍 Running linters..."
	cd backend && black app/ --check
	cd backend && isort app/ --check-only
	cd backend && flake8 app/
	cd frontend && npm run lint

lint-fix:
	cd backend && black app/
	cd backend && isort app/
	cd frontend && npm run lint -- --fix

# Docker
build:
	@echo "🏗️  Building Docker images..."
	cd backend && docker-compose build --no-cache

up:
	@echo "🚀 Starting production containers..."
	cd backend && docker-compose up -d

down:
	@echo "🛑 Stopping containers..."
	cd backend && docker-compose down

logs:
	docker-compose -f backend/docker-compose.dev.yml logs -f

logs-backend:
	docker-compose -f backend/docker-compose.dev.yml logs -f backend

logs-celery:
	docker-compose -f backend/docker-compose.dev.yml logs -f celery_worker

# Database
migrate:
	cd backend && alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"

db-up:
	docker-compose -f backend/docker-compose.dev.yml up -d db redis

db-down:
	docker-compose -f backend/docker-compose.dev.yml stop db redis

# Celery
celery:
	cd backend && celery -A app.celery_app.celery_app worker --loglevel=info

celery-beat:
	cd backend && celery -A app.celery_app.celery_app beat --loglevel=info

flower:
	cd backend && celery -A app.celery_app.celery_app flower --port=5555

# VPS Setup (run as root)
setup-vps:
	@echo "⚠️  This will configure the VPS!"
	@if [ "$$(whoami)" != "root" ]; then \
		echo "❌ Must be run as root"; \
		exit 1; \
	fi
	@read -p "Enter your domain: " domain; \
	./setup-vps.sh $$domain

# Deployment (run as podcast user)
deploy:
	@echo "🚀 Deploying to production..."
	@if [ "$$(whoami)" = "root" ]; then \
		echo "❌ Do not run as root. Use: su - podcast"; \
		exit 1; \
	fi
	@read -p "Enter your domain: " domain; \
	./deploy-production.sh $$domain

# Backup
backup:
	@echo "💾 Creating backup..."
	@mkdir -p backups
	@DATE=$$(date +%Y%m%d_%H%M%S); \
	cd backend && docker-compose exec -T db pg_dump -U postgres podcast_db > ../backups/db_$$DATE.sql; \
	tar -czf backups/uploads_$$DATE.tar.gz backend/uploads/; \
	echo "✅ Backup created: backups/db_$$DATE.sql"

# Update
update:
	@echo "⬆️  Updating to latest version..."
	git pull origin main
	cd backend && docker-compose pull
	cd backend && docker-compose up -d
	docker system prune -f
	@echo "✅ Update complete!"

# Monitoring
status:
	cd backend && docker-compose ps

health:
	@curl -s http://localhost:8000/health | jq . || curl http://localhost:8000/health

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f backend/docker-compose.dev.yml down -v
	docker system prune -f
