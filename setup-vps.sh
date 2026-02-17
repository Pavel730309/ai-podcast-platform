#!/bin/bash
#
# AI Podcast Platform - VPS Setup Script
# Run as root on fresh Ubuntu 22.04 server
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-podcast-platform"
USER_NAME="podcast"
DOMAIN="${1:-}"

echo -e "${BLUE}🚀 AI Podcast Platform - VPS Setup${NC}"
echo "=================================="

if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}⚠️  Usage: ./setup-vps.sh your-domain.com${NC}"
    echo "Example: ./setup-vps.sh podcast.example.com"
    exit 1
fi

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root${NC}"
    exit 1
fi

echo -e "\n${GREEN}📋 Setup Configuration:${NC}"
echo "Domain: $DOMAIN"
echo "User: $USER_NAME"
echo ""

# 1. System Update
echo -e "${BLUE}⬆️  Updating system...${NC}"
apt update && apt upgrade -y
apt install -y curl wget git vim htop ufw fail2ban software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# 2. Create user
echo -e "\n${BLUE}👤 Creating user $USER_NAME...${NC}"
if id "$USER_NAME" &>/dev/null; then
    echo "User already exists"
else
    useradd -m -s /bin/bash "$USER_NAME"
    usermod -aG sudo "$USER_NAME"
    echo -e "${GREEN}✅ User $USER_NAME created${NC}"
fi

# 3. Setup SSH keys
echo -e "\n${BLUE}🔑 Setting up SSH...${NC}"
if [ -f /root/.ssh/authorized_keys ]; then
    mkdir -p /home/$USER_NAME/.ssh
    cp /root/.ssh/authorized_keys /home/$USER_NAME/.ssh/
    chown -R $USER_NAME:$USER_NAME /home/$USER_NAME/.ssh
    chmod 700 /home/$USER_NAME/.ssh
    chmod 600 /home/$USER_NAME/.ssh/authorized_keys
    echo -e "${GREEN}✅ SSH keys copied${NC}"
fi

# 4. Configure Firewall
echo -e "\n${BLUE}🛡️  Configuring firewall...${NC}"
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5555/tcp  # Flower
ufw --force enable
echo -e "${GREEN}✅ Firewall configured${NC}"

# 5. Configure Fail2Ban
echo -e "\n${BLUE}🛡️  Configuring Fail2Ban...${NC}"
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban
echo -e "${GREEN}✅ Fail2Ban configured${NC}"

# 6. Install Docker
echo -e "\n${BLUE}🐳 Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $USER_NAME
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo "Docker already installed"
fi

# 7. Install Docker Compose
echo -e "\n${BLUE}🐳 Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    DOCKER_CONFIG=${DOCKER_CONFIG:-/root/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
    
    # Also for user
    mkdir -p /home/$USER_NAME/.docker/cli-plugins
    cp $DOCKER_CONFIG/cli-plugins/docker-compose /home/$USER_NAME/.docker/cli-plugins/
    chown -R $USER_NAME:$USER_NAME /home/$USER_NAME/.docker
    
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo "Docker Compose already installed"
fi

# 8. Install Nginx
echo -e "\n${BLUE}🌐 Installing Nginx...${NC}"
apt install -y nginx
systemctl enable nginx
echo -e "${GREEN}✅ Nginx installed${NC}"

# 9. Install Certbot
echo -e "\n${BLUE}🔒 Installing Certbot...${NC}"
apt install -y certbot python3-certbot-nginx
echo -e "${GREEN}✅ Certbot installed${NC}"

# 10. Create project directory
echo -e "\n${BLUE}📁 Creating project directory...${NC}"
PROJECT_DIR="/home/$USER_NAME/$PROJECT_NAME"
mkdir -p $PROJECT_DIR
chown $USER_NAME:$USER_NAME $PROJECT_DIR

# 11. Create swap (if RAM < 4GB)
TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM" -lt 4096 ]; then
    echo -e "\n${BLUE}💾 Creating swap file...${NC}"
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo -e "${GREEN}✅ Swap created${NC}"
fi

# 12. Configure sysctl
echo -e "\n${BLUE}⚙️  Optimizing system...${NC}"
cat >> /etc/sysctl.conf << EOF
# Docker optimization
vm.overcommit_memory = 1
vm.swappiness = 10
net.core.somaxconn = 65535
EOF
sysctl -p

# 13. Create backup directory
mkdir -p /backups
chown $USER_NAME:$USER_NAME /backups

# 14. Setup log rotation
cat > /etc/logrotate.d/$PROJECT_NAME << EOF
/home/$USER_NAME/$PROJECT_NAME/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 $USER_NAME $USER_NAME
}
EOF

# Summary
echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}✅ VPS Setup Complete!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Switch to user: su - $USER_NAME"
echo "2. Clone repository: git clone <your-repo> $PROJECT_NAME"
echo "3. Copy deploy script and run: ./deploy-production.sh $DOMAIN"
echo ""
echo -e "${BLUE}Server info:${NC}"
echo "Domain: $DOMAIN"
echo "User: $USER_NAME"
echo "RAM: ${TOTAL_RAM}MB"
echo "Docker: $(docker --version)"
echo ""
