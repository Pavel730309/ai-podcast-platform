# 🖥️ Инструкция по размещению на VPS

## 📋 Предварительные требования

1. **VPS сервер** с Ubuntu 22.04 LTS (рекомендуется Hetzner CX21 или аналогичный)
2. **Доменное имя** (например, podcast.yourdomain.com)
3. **Доступ root к серверу**
4. **DNS настроены** для указания на IP вашего VPS
5. **API ключи** для OpenAI и ElevenLabs (опционально)

## 🚀 Шаги размещения

### Шаг 1: Подготовка VPS

1. Подключитесь к серверу как root:
```bash
ssh root@YOUR_VPS_IP
```

2. Загрузите и запустите скрипт настройки:
```bash
wget https://raw.githubusercontent.com/Pavel-Perm/ai-podcast-platform/main/setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh your-domain.com
```

### Шаг 2: Переключение на пользователя podcast

После завершения скрипта настройки:
```bash
su - podcast
```

### Шаг 3: Деплой приложения

1. Загрузите скрипт деплоя:
```bash
wget https://raw.githubusercontent.com/Pavel-Perm/ai-podcast-platform/main/deploy-production.sh
chmod +x deploy-production.sh
```

2. Запустите деплой:
```bash
./deploy-production.sh your-domain.com
```

### Шаг 4: Настройка .env файла

После запуска деплоя, необходимо отредактировать файл `.env`:
```bash
nano ~/ai-podcast-platform/backend/.env
```

Добавьте обязательные API ключи:
- `OPENAI_API_KEY` - ваш API ключ от OpenAI
- `ELEVENLABS_API_KEY` - ваш API ключ от ElevenLabs (опционально)
- `POSTGRES_PASSWORD` - пароль для PostgreSQL

### Шаг 5: Проверка работы

После завершения деплоя проверьте работу:
```bash
# Проверка статуса контейнеров
docker-compose ps

# Проверка логов
docker-compose logs -f

# Проверка здоровья
curl https://your-domain.com/health
```

## 📦 Структура развертывания

### Контейнеры
- **backend** - FastAPI приложение
- **db** - PostgreSQL база данных
- **redis** - Redis для очередей
- **celery_worker** - Celery worker для фоновых задач
- **celery_beat** - Celery beat для задач по расписанию
- **nginx** - Reverse proxy

### Порты
- **80** - HTTP (перенаправление на HTTPS)
- **443** - HTTPS
- **5555** - Flower (Celery dashboard)

### Директории
- `/home/podcast/ai-podcast-platform` - корневая директория проекта
- `/home/podcast/ai-podcast-platform/backend/uploads` - загруженные файлы
- `/home/podcast/ai-podcast-platform/backend/cache` - кэш
- `/backups` - бэкапы

## 🔒 Безопасность

### Firewall
- Разрешены только порты 22 (SSH), 80 (HTTP), 443 (HTTPS)
- Установлен Fail2Ban для защиты от брутфорса

### SSL
- Установлен Let's Encrypt SSL сертификат
- Автоматическое обновление сертификатов

### Доступ
- Доступ только через SSH ключи
- Отдельный пользователь `podcast` без прав root

## 🛠️ Управление

### Полезные команды

```bash
# Просмотр логов
docker-compose logs -f

# Перезапуск сервисов
docker-compose restart

# Остановка сервисов
docker-compose down

# Запуск сервисов
docker-compose up -d

# Обновление приложения
git pull && docker-compose up -d --build

# Проверка состояния
docker-compose ps

# Проверка здоровья
curl https://your-domain.com/health
```

## 📊 Мониторинг

### Health check
Доступен по адресу: `https://your-domain.com/health`

### Celery Flower
Доступен по адресу: `http://your-domain.com:5555`

### Логи
Логи находятся в директории `/home/podcast/ai-podcast-platform/backend/logs/`

## 🔄 Обновление

Для обновления приложения:
```bash
cd ~/ai-podcast-platform/backend
git pull
docker-compose up -d --build
```

## 📋 Чек-лист готовности

- [ ] VPS сервер куплен и настроен
- [ ] Домен привязан к IP VPS
- [ ] SSH ключи настроены
- [ ] Docker установлен
- [ ] Проект склонирован
- [ ] .env настроен с API ключами
- [ ] SSL сертификат получен
- [ ] Контейнеры запущены
- [ ] Health check проходит
- [ ] Бэкапы настроены

## 🆘 Устранение неполадок

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

## 📈 Стоимость развертывания

| Компонент | Цена/мес |
|-----------|----------|
| VPS (Hetzner CX21) | €5.35 (~$6) |
| Домен (.com) | $10-15/год |
| SSL (Let's Encrypt) | Бесплатно |
| **Итого** | **~$6-7/мес** |

## 🎯 Готово!

После выполнения всех шагов ваш AI Podcast Platform будет доступен по адресу `https://your-domain.com`.