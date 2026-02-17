#!/bin/bash

# AI Podcast Platform - Production Deployment Script
# Usage: ./deploy.sh [environment]
# Environments: local, staging, production

set -e

ENV=${1:-production}
COMPOSE_FILE="docker-compose.yml"

echo "🚀 Deploying AI Podcast Platform to $ENV environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  Warning: OPENAI_API_KEY not set${NC}"
fi

# Pull latest images
echo "📦 Pulling latest images..."
docker-compose -f $COMPOSE_FILE pull

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose -f $COMPOSE_FILE up -d --build

# Wait for database
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose -f $COMPOSE_FILE exec -T backend alembic upgrade head || echo "Migrations skipped"

# Health check
echo "🏥 Checking service health..."
attempt=0
max_attempts=30

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Services are healthy!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "  Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ Services failed to start${NC}"
    docker-compose -f $COMPOSE_FILE logs backend
    exit 1
fi

# Cleanup
echo "🧹 Cleaning up old images..."
docker system prune -f

echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo ""
echo "📱 Application URLs:"
echo "   Frontend: http://localhost"
echo "   API Docs: http://localhost/api/docs"
echo "   Flower:   http://localhost:5555"
echo ""
echo "📊 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""
