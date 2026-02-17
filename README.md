# AI Podcast Platform

AI Podcast Platform - это веб-приложение для автоматического создания аудио-подкастов из текстовых материалов с использованием искусственного интеллекта. Система преобразует текстовые материалы в диалоговые подкасты с естественной речью, фоновой музыкой и обложками.

## 🚀 Особенности

- **Извлечение текста** из PDF, DOCX и URL
- **AI-генерация сценариев** для подкастов
- **Синтез речи** с помощью OpenAI, ElevenLabs и Google TTS
- **Аудио-обработка** с фоновой музыкой и эффектами
- **Генерация обложек** с помощью AI-генераторов
- **RSS-генератор** для публикации на платформах подкастов
- **Адаптивный веб-интерфейс** на React + TypeScript

## 🛠️ Технологии

### Backend
- Python 3.11
- FastAPI
- PostgreSQL
- Redis
- Celery
- Docker

### Frontend
- React.js
- TypeScript
- Tailwind CSS

## 📁 Структура проекта

```
.
├── backend/                 # Backend API
│   ├── app/                 # Приложение
│   │   ├── api/             # API эндпоинты
│   │   ├── services/        # Сервисы обработки
│   │   ├── models/          # Модели данных
│   │   └── tasks/           # Асинхронные задачи
│   ├── tests/               # Тесты
│   └── Dockerfile           # Docker файл
├── frontend/                # Frontend приложение
│   └── src/                 # Исходный код React
├── docs/                    # Документация
└── deploy/                  # Скрипты деплоя
```

## 🚀 Быстрый старт

### Локальный запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Pavel-Perm/ai-podcast-platform.git
cd ai-podcast-platform
```

2. Скопируйте и настройте конфигурационные файлы:
```bash
cd backend
cp .env.example .env
# Отредактируйте .env для добавления API ключей
```

3. Запустите приложение с помощью Docker Compose:
```bash
docker-compose up --build
```

4. Откройте в браузере:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/api/docs
- Celery Flower: http://localhost:5555

## 📦 Деплой

Для деплоя на VPS используйте предоставленные скрипты:
- `setup-vps.sh` - настройка сервера
- `deploy-production.sh` - деплой приложения

## 📚 Документация

- [Техническое задание](docs/technical_specification.md)
- [Архитектура системы](docs/architecture.md)
- [Руководство по деплою](DEPLOY_GUIDE.md)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для ваших изменений (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - смотрите файл LICENSE для подробностей.
