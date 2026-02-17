# 🚀 Полное руководство по деплою AI Podcast Platform на VPS

## Содержание
1. [Выбор VPS](#1-выбор-vps)
2. [Подготовка сервера](#2-подготовка-сервера)
3. [Установка зависимостей](#3-установка-зависимостей)
4. [Настройка проекта](#4-настройка-проекта)
5. [SSL сертификаты](#5-ssl-сертификаты)
6. [Запуск](#6-запуск)
7. [Мониторинг](#7-мониторинг)
8. [Бэкапы](#8-бэкапы)

---

## 1. Выбор VPS

### Рекомендуемые провайдеры:

| Провайдер | Цена | CPU | RAM | SSD | Локация |
|-----------|------|-----|-----|-----|---------|
| **Hetzner CX21** | €5.35/мес | 2 vCPU | 4 GB | 40 GB | Германия/Финляндия |
| **DigitalOcean Basic** | $6/мес | 1 vCPU | 512 MB | 10 GB | США/Европа |
| **Vultr Cloud** | $5/мес | 1 vCPU | 1 GB | 25 GB | Много локаций |
| **Yandex Cloud** | ~300₽/мес | 2 vCPU | 2 GB | 20 GB | Россия |

### Минимальные требования:
- **CPU**: 2 ядра
- **RAM**: 4 GB (можно 2 GB + swap)
- **SSD**: 40 GB
- **OS**: Ubuntu 22.04 LTS
- **Порты**: 22 (SSH), 80 (HTTP), 443 (HTTPS)

---

## 2. Подготовка сервера

### 2.1 Подключение к VPS

```bash
# Подключение по SSH
ssh root@YOUR_SERVER_IP

# Или с ключом
ssh -i ~/.ssh/id_rsa root@YOUR_SERVER_IP
```

### 2.2 Обновление системы

```bash
# Обновление пакетов
apt update && apt upgrade -y

# Установка базовых утилит
apt install -y curl wget git vim htop ufw fail2ban
```

### 2.3 Настройка firewall

```bash
# Настройка UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5555/tcp  # Flower

# Включение firewall
ufw --force enable

# Проверка статуса
ufw status verbose
```

### 2.4 Создание пользователя (не root)

```bash
# Создание пользователя
useradd -m -s /bin/bash podcast
usermod -aG sudo podcast

# Установка пароля
passwd podcast

# Настройка SSH ключей
mkdir -p /home/podcast/.ssh
cp /root/.ssh/authorized_keys /home/podcast/.ssh/
chown -R podcast:podcast /home/podcast/.ssh
chmod 700 /home/podcast/.ssh
chmod 600 /home/podcast/.ssh/authorized_keys
```

### 2.5 Настройка SSH (безопасность)

```bash
# Редактирование конфига SSH
vim /etc/ssh/sshd_config

# Изменить следующие строки:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3

# Перезапуск SSH
systemctl restart sshd
```

---

## 3. Установка зависимостей

### 3.1 Docker и Docker Compose

```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Добавление пользователя в группу docker
usermod -aG docker podcast

# Установка Docker Compose
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# Проверка
docker --version
docker compose version
```

### 3.2 Установка Certbot (Let's Encrypt)

```bash
apt install -y certbot python3-certbot-nginx
```

---

## 4. Настройка проекта

### 4.1 Клонирование репозитория

```bash
# Переключение на пользователя podcast
su - podcast

# Клонирование проекта
git clone https://github.com/yourusername/ai-podcast-platform.git
cd ai-podcast-platform
```

### 4.2 Настройка окружения

```bash
cd backend

# Копирование конфига
cp .env.example .env

# Редактирование (используйте nano или vim)
nano .env
```

**Заполните .env:**

```env
# Database
POSTGRES_DB=podcast_db
POSTGRES_USER=podcast
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD_HERE

# API Keys (обязательно!)
OPENAI_API_KEY=sk-your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Security
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false

# Domain (для SSL)
DOMAIN=your-domain.com
```

### 4.3 Настройка Nginx

```bash
# Для домена (замените your-domain.com)
sudo vim /etc/nginx/sites-available/podcast
```

**Конфигурация:**

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /uploads {
        alias /home/podcast/ai-podcast-platform/backend/uploads;
        expires 30d;
    }
}
```

```bash
# Активация сайта
sudo ln -s /etc/nginx/sites-available/podcast /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 5. SSL сертификаты

### 5.1 Получение сертификата Let's Encrypt

```bash
# Установка certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автообновление
sudo systemctl status certbot.timer
```

### 5.2 Проверка SSL

```bash
# Тест SSL
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Проверка автоматического обновления
sudo certbot renew --dry-run
```

---

## 6. Запуск

### 6.1 Запуск проекта

```bash
cd ~/ai-podcast-platform/backend

# Production запуск
docker-compose up -d

# Или через скрипт
./deploy.sh production
```

### 6.2 Проверка статуса

```bash
# Статус контейнеров
docker-compose ps

# Логи
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Health check
curl https://your-domain.com/health
```

### 6.3 Выполнение миграций

```bash
docker-compose exec backend alembic upgrade head
```

---

## 7. Мониторинг

### 7.1 Установка Prometheus + Grafana

```bash
# Создание сети
docker network create monitoring

# Prometheus
docker run -d \
  --name=prometheus \
  --network=monitoring \
  -p 9090:9090 \
  -v /opt/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus

# Grafana
docker run -d \
  --name=grafana \
  --network=monitoring \
  -p 3000:3000 \
  -v grafana-storage:/var/lib/grafana \
  grafana/grafana
```

### 7.2 Дашборды Grafana

- Импортируйте dashboard ID: **1860** (Node Exporter)
- Создайте dashboard для приложения

### 7.3 Алерты

Настройте алерты в Grafana для:
- CPU > 80%
- Memory > 80%
- Disk > 80%
- API down

---

## 8. Бэкапы

### 8.1 Автоматические бэкапы

```bash
# Создание скрипта бэкапа
sudo vim /opt/backup/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Бэкап базы данных
docker exec podcast_db pg_dump -U podcast podcast_db > $BACKUP_DIR/db_$DATE.sql

# Бэкап uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /home/podcast/ai-podcast-platform/backend/uploads

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /opt/backup/backup.sh

# Cron job (каждый день в 2:00)
0 2 * * * /opt/backup/backup.sh
```

### 8.2 Бэкап на внешний сервер (опционально)

```bash
# Настройка rsync
rsync -avz /backups/ user@backup-server:/backups/podcast/
```

---

## 🆘 Troubleshooting

### Проблема: Контейнеры не запускаются

```bash
# Проверка логов
docker-compose logs

# Пересборка
docker-compose down
docker-compose up --build -d
```

### Проблема: SSL не работает

```bash
# Перевыпуск сертификата
sudo certbot renew --force-renewal
sudo systemctl restart nginx
```

### Проблема: Permission denied

```bash
# Исправление прав
sudo chown -R podcast:podcast /home/podcast/ai-podcast-platform
```

---

## ✅ Чек-лист деплоя

- [ ] VPS куплен и настроен
- [ ] Домен привязан к IP
- [ ] SSH ключи настроены
- [ ] Docker установлен
- [ ] Проект склонирован
- [ ] .env настроен с API ключами
- [ ] SSL сертификат получен
- [ ] Контейнеры запущены
- [ ] Health check проходит
- [ ] Мониторинг настроен
- [ ] Бэкапы настроены

---

## 📞 Поддержка

При проблемах:
1. Проверьте логи: `docker-compose logs`
2. Проверьте статус: `docker-compose ps`
3. Проверьте ресурсы: `htop`, `df -h`

**Готово к production!** 🚀
