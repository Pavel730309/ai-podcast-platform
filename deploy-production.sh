#!/bin/bash
#
# AI Podcast Platform - Production Deploy Script
# Run as podcast user after setup-vps.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DOMAIN="${1:-}"
REPO_URL="${2:-https://github.com/yourusername/ai-podcast-platform.git}"

echo -e "${BLUE}🚀 AI Podcast Platform - Production Deploy${NC}"
echo "=========================================="

if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}⚠️  Usage: ./deploy-production.sh your-domain.com [repo-url]${NC}"
    exit 1
fi

# Check if running as podcast user
if [ "$USER" != "podcast" ]; then
    echo -e "${RED}❌ Please run as 'podcast' user${NC}"
    echo "Run: su - podcast"
    exit 1
fi

PROJECT_DIR="$HOME/ai-podcast-platform"

echo -e "\n${GREEN}📋 Deploy Configuration:${NC}"
echo "Domain: $DOMAIN"
echo "Repo: $REPO_URL"
echo "User: $USER"
echo ""

# 1. Clone or update repository
echo -e "${BLUE}📥 Getting project files...${NC}"
if [ -d "$PROJECT_DIR" ]; then
    echo "Project exists, updating..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi
echo -e "${GREEN}✅ Project ready${NC}"

# 2. Setup environment
echo -e "\n${BLUE}⚙️  Setting up environment...${NC}"
cd "$PROJECT_DIR/backend"

if [ ! -f .env ]; then
    cp .env.example .env
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update .env
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    sed -i "s/DEBUG=.*/DEBUG=false/" .env
    sed -i "s/your-domain.com/$DOMAIN/g" .env
    
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit .env file and add your API keys!${NC}"
    echo "Run: nano $PROJECT_DIR/backend/.env"
    echo ""
    echo "Required:"
    echo "  - OPENAI_API_KEY"
    echo "  - ELEVENLABS_API_KEY (optional)"
    echo "  - POSTGRES_PASSWORD"
    echo ""
    
    # Wait for user
    read -p "Press Enter after you've configured .env file..."
fi

echo -e "${GREEN}✅ Environment configured${NC}"

# 3. Create necessary directories
echo -e "\n${BLUE}📁 Creating directories...${NC}"
mkdir -p uploads cache logs data/music
echo -e "${GREEN}✅ Directories created${NC}"

# 4. Setup Nginx
echo -e "\n${BLUE}🌐 Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/podcast > /dev/null << EOF
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /uploads {
        alias $PROJECT_DIR/backend/uploads;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /health {
        proxy_pass http://backend/health;
        access_log off;
    }
}
EOF

# Enable site
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/podcast /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t && sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx configured${NC}"

# 5. Setup SSL
echo -e "\n${BLUE}🔒 Setting up SSL...${NC}"
if ! sudo certbot certificates | grep -q "$DOMAIN"; then
    sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN
    echo -e "${GREEN}✅ SSL certificate installed${NC}"
else
    echo "SSL certificate already exists"
fi

# Auto-renewal test
sudo certbot renew --dry-run

# 6. Build and start Docker containers
echo -e "\n${BLUE}🐳 Building and starting containers...${NC}"
docker-compose down 2>/dev/null || true
docker-compose pull
docker-compose build --no-cache
docker-compose up -d

# 7. Wait for database
echo -e "\n${BLUE}⏳ Waiting for database...${NC}"
sleep 10

# 8. Run migrations
echo -e "\n${BLUE}🔄 Running migrations...${NC}"
docker-compose exec -T backend alembic upgrade head || echo "Migrations may have already run"

# 9. Health check
echo -e "\n${BLUE}🏥 Health check...${NC}"
attempt=0
max_attempts=30

while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Application is healthy!${NC}"
        break
    fi
    attempt=$((attempt + 1))
    echo "  Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ Application failed to start${NC}"
    echo "Check logs: docker-compose logs"
    exit 1
fi

# 10. Cleanup
echo -e "\n${BLUE}🧹 Cleaning up...${NC}"
docker system prune -f
echo -e "${GREEN}✅ Cleanup complete${NC}"

# Summary
echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${BLUE}📱 Your Application:${NC}"
echo "  Website: https://$DOMAIN"
echo "  API Docs: https://$DOMAIN/api/docs"
echo "  Flower: http://$DOMAIN:5555"
echo ""
echo -e "${BLUE}🛠️  Useful Commands:${NC}"
echo "  View logs:    cd $PROJECT_DIR/backend && docker-compose logs -f"
echo "  Restart:      docker-compose restart"
echo "  Stop:         docker-compose down"
echo "  Update:       git pull && docker-compose up -d --build"
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo "  Check status: docker-compose ps"
echo "  Health:       curl https://$DOMAIN/health"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Test creating a podcast through the web interface"
echo "2. Check Flower dashboard for task processing"
echo "3. Setup backups (see BACKUP_GUIDE.md)"
echo ""
