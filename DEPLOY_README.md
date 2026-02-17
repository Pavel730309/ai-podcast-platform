# 🚀 Деплой-комплект готов!

## Дата: 16.02.2026
## Статус: ✅ ГОТОВО К ПРОДАКШЕНУ

---

## 📦 Что создано

### 1. 📚 Полное руководство по деплою
**Файл:** `DEPLOY_GUIDE.md`

Содержит:
- Выбор VPS (Hetzner, DigitalOcean, Vultr, Yandex)
- Подготовка сервера (Ubuntu 22.04)
- Установка Docker, Nginx, SSL
- Настройка firewall и безопасности
- Мониторинг и бэкапы
- Troubleshooting

### 2. 🤖 Автоматические скрипты

#### `setup-vps.sh` - Настройка свежего VPS
- Обновление системы
- Создание пользователя `podcast`
- Настройка SSH и firewall
- Установка Docker и Docker Compose
- Установка Nginx и Certbot
- Настройка fail2ban
- Создание swap (если нужно)

**Запуск:**
```bash
ssh root@YOUR_VPS_IP
wget https://raw.githubusercontent.com/yourrepo/main/setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh your-domain.com
```

#### `deploy-production.sh` - Деплой приложения
- Клонирование/обновление репозитория
- Настройка .env
- Настройка Nginx
- Получение SSL сертификата
- Запуск Docker контейнеров
- Health check

**Запуск:**
```bash
su - podcast
./deploy-production.sh your-domain.com
```

### 3. ⚙️ GitHub Actions автодеплой
**Файл:** `.github/workflows/deploy.yml`

Включает:
- Автоматическое тестирование (pytest)
- Сборка и пуш Docker образов
- Автодеплой на VPS
- Уведомления в Slack

**Настройка:** см. `GITHUB_ACTIONS_SETUP.md`

### 4. 📋 Инструкция по GitHub Actions
**Файл:** `GITHUB_ACTIONS_SETUP.md`

Пошаговая настройка:
- GitHub Secrets
- SSH ключи
- Docker Hub
- Тест автодеплоя

### 5. 🔧 Обновленный Makefile
Новые команды:
```bash
make setup-vps     # Настройка VPS
make deploy        # Деплой
make backup        # Бэкап
make update        # Обновление
make health        # Проверка здоровья
```

---

## 🎯 Как использовать

### Вариант 1: Ручной деплой (рекомендуется для первого раза)

```bash
# 1. Купите VPS (Hetzner CX21 - €5.35/мес)
# 2. Получите root доступ

# 3. На VPS (как root):
ssh root@YOUR_VPS_IP
wget https://your-repo/setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh podcast.yourdomain.com

# 4. На VPS (как podcast):
su - podcast
./deploy-production.sh podcast.yourdomain.com

# 5. Готово! Откройте https://podcast.yourdomain.com
```

### Вариант 2: Автоматический деплой (GitHub Actions)

```bash
# 1. Настройте secrets в GitHub (см. GITHUB_ACTIONS_SETUP.md)
# 2. Push в main:
git push origin main

# 3. Откройте GitHub → Actions → наблюдайте за деплоем
# 4. Через 3-5 минут сайт обновится автоматически
```

### Вариант 3: Через Makefile

```bash
# Локально - запустить тесты
make test

# На VPS (как root) - настройка
make setup-vps

# На VPS (как podcast) - деплой
make deploy

# Обновление
make update

# Бэкап
make backup
```

---

## 💰 Стоимость

| Компонент | Цена/мес |
|-----------|----------|
| VPS (Hetzner CX21) | €5.35 (~$6) |
| Домен (.com) | $10-15/год |
| SSL (Let's Encrypt) | Бесплатно |
| Docker Hub | Бесплатно |
| **Итого** | **~$6-7/мес** |

---

## 🔐 Безопасность

Включено:
- ✅ Firewall (UFW)
- ✅ Fail2Ban (защита от брутфорса)
- ✅ SSH только по ключу
- ✅ SSL сертификаты
- ✅ Отдельный пользователь (не root)
- ✅ Автообновление SSL
- ✅ Бэкапы

---

## 📊 Мониторинг

Доступно:
- Health check: `https://your-domain.com/health`
- Flower (Celery): `http://your-domain.com:5555`
- Docker: `docker-compose ps`
- Логи: `make logs`

---

## ✅ Чек-лист перед деплоем

- [ ] Куплен VPS (2 vCPU, 4GB RAM, 40GB SSD)
- [ ] Куплен домен и направлен на VPS IP
- [ ] Получен OpenAI API ключ
- [ ] (Опционально) Получен ElevenLabs API ключ
- [ ] GitHub репозиторий создан
- [ ] Docker Hub аккаунт создан

---

## 🚀 Быстрый старт (копировать и вставить)

```bash
# === ШАГ 1: На вашем компьютере ===
# Купите VPS на Hetzner: https://www.hetzner.com/cloud
# Создайте сервер (CX21, Ubuntu 22.04)
# Скопируйте IP адрес

# === ШАГ 2: Подключение к VPS ===
ssh root@YOUR_VPS_IP

# === ШАГ 3: Установка (на VPS как root) ===
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ai-podcast-platform/main/setup-vps.sh -o setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh your-domain.com

# === ШАГ 4: Деплой (на VPS как podcast) ===
su - podcast
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/ai-podcast-platform/main/deploy-production.sh -o deploy-production.sh
chmod +x deploy-production.sh
./deploy-production.sh your-domain.com

# === ШАГ 5: Готово! ===
# Откройте https://your-domain.com в браузере
```

---

## 🎉 Итог

**Создано:**
- ✅ Полное руководство по деплою
- ✅ 2 автоматических скрипта
- ✅ GitHub Actions workflow
- ✅ Инструкция по настройке
- ✅ Обновленный Makefile

**Результат:**
- 💰 Стоимость: ~$6-7/мес
- ⏱️ Время деплоя: 10-15 минут
- 🔐 Безопасность: production-ready
- 🤖 Автоматизация: push → deploy

**Проект полностью готов к production!** 🚀

Можно покупать VPS и деплоить!
