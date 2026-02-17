# 🤖 Автоматический деплой через GitHub Actions

## Быстрый старт

### 1. Добавьте Secrets в GitHub

Перейдите в `Settings → Secrets and variables → Actions` и добавьте:

#### Обязательные secrets:

| Secret | Описание | Где взять |
|--------|----------|-----------|
| `VPS_HOST` | IP адрес вашего VPS | Из панели управления VPS |
| `VPS_USERNAME` | Имя пользователя | Обычно `podcast` |
| `VPS_SSH_KEY` | Приватный SSH ключ | `cat ~/.ssh/id_rsa` на VPS |
| `DOCKER_USERNAME` | Логин Docker Hub | dockerhub.com |
| `DOCKER_PASSWORD` | Пароль Docker Hub | dockerhub.com |
| `DOMAIN` | Ваш домен | Например `podcast.example.com` |

#### Опциональные secrets:

| Secret | Описание |
|--------|----------|
| `SLACK_WEBHOOK_URL` | Для уведомлений в Slack |

### 2. Генерация SSH ключа

На вашем VPS выполните:

```bash
# От имени пользователя podcast
su - podcast

# Генерация ключа
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions

# Показать публичный ключ
cat ~/.ssh/github_actions.pub

# Добавить в authorized_keys
cat ~/.ssh/github_actions.pub >> ~/.ssh/authorized_keys

# Показать приватный ключ (скопируйте в GitHub Secrets)
cat ~/.ssh/github_actions
```

**⚠️ Важно:** Приватный ключ (начинается с `-----BEGIN RSA PRIVATE KEY-----`) добавьте в `VPS_SSH_KEY`

### 3. Добавьте публичный ключ на VPS

```bash
# На VPS
sudo mkdir -p /root/.ssh
sudo chmod 700 /root/.ssh

# Добавьте публичный ключ GitHub Actions
echo "ssh-rsa AAAAB3..." | sudo tee -a /root/.ssh/authorized_keys
sudo chmod 600 /root/.ssh/authorized_keys
```

### 4. Docker Hub

1. Зарегистрируйтесь на [hub.docker.com](https://hub.docker.com)
2. Создайте репозитории:
   - `ai-podcast-backend`
   - `ai-podcast-frontend`
3. Скопируйте логин и пароль в GitHub Secrets

### 5. Тест автодеплоя

```bash
# Сделайте push в main
git add .
git commit -m "Test deployment"
git push origin main

# Откройте GitHub → Actions и наблюдайте за процессом
```

---

## Как это работает

```
Push to main
    │
    ▼
GitHub Actions
    │
    ├── 1. Run tests (pytest)
    │
    ├── 2. Build Docker images
    │   └── Push to Docker Hub
    │
    └── 3. Deploy to VPS
        ├── SSH to VPS
        ├── git pull
        ├── docker-compose pull
        └── docker-compose up -d
```

---

## Troubleshooting

### Ошибка: Permission denied (SSH)

```bash
# Проверьте права на VPS
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Проверьте формат ключа (должен быть в одну строку в GitHub)
```

### Ошибка: Docker login failed

```bash
# Проверьте логин и пароль в secrets
# Убедитесь, что репозитории созданы на Docker Hub
```

### Ошибка: Tests failed

```bash
# Проверьте тесты локально
cd backend
pytest -v
```

---

## Ручной деплой (если автоматика не работает)

```bash
# На VPS
su - podcast
cd ~/ai-podcast-platform
git pull origin main
cd backend
docker-compose pull
docker-compose up -d
```

## 🎉 Готово!

Теперь каждый push в `main` будет автоматически деплоиться на ваш VPS!
