# 🐳 Инструкция по созданию и загрузке Docker образа

## Описание образа

Docker образ для AI Podcast Platform содержит:
- Python 3.11 runtime
- Все необходимые зависимости для работы приложения
- Установленные библиотеки для обработки аудио, текста и работы с API
- Оптимизированная среда для запуска FastAPI приложения

## 🛠️ Шаги по созданию образа

### 1. Проверка требований

Перед созданием образа убедитесь, что у вас установлен:
- Docker Desktop или Docker Engine
- Git (для клонирования проекта)

### 2. Клонирование проекта

```bash
git clone https://github.com/Pavel-Perm/ai-podcast-platform.git
cd ai-podcast-platform
```

### 3. Создание Docker образа

Используйте следующую команду для создания образа:

```bash
docker build -t ai-podcast-platform:latest ./backend
```

Или для создания с конкретным тегом:

```bash
docker build -t pavel-perm/ai-podcast-platform:v1.0.0 ./backend
```

### 4. Проверка образа

После создания проверьте, что образ создан:

```bash
docker images | grep ai-podcast-platform
```

### 5. Запуск контейнера локально (для тестирования)

```bash
docker run -d \
  --name ai-podcast-platform \
  -p 8000:8000 \
  -v $(pwd)/backend/uploads:/app/uploads \
  -v $(pwd)/backend/cache:/app/cache \
  pavel-perm/ai-podcast-platform:v1.0.0
```

### 6. Загрузка образа в Docker Hub

#### 6.1. Вход в Docker Hub

```bash
docker login
```

Введите свои учетные данные Docker Hub.

#### 6.2. Тегирование образа

```bash
docker tag ai-podcast-platform:latest pavel-perm/ai-podcast-platform:latest
docker tag ai-podcast-platform:latest pavel-perm/ai-podcast-platform:v1.0.0
```

#### 6.3. Пуш образа

```bash
docker push pavel-perm/ai-podcast-platform:latest
docker push pavel-perm/ai-podcast-platform:v1.0.0
```

## 📦 Структура Docker образа

### Системные зависимости
- gcc, g++, libpq-dev, libffi-dev (для компиляции библиотек)
- libsndfile1, libsox-fmt-mp3, sox (для аудио обработки)

### Python зависимости
- FastAPI, uvicorn (web framework)
- SQLAlchemy, asyncpg (database)
- Redis, Celery (queue)
- PyPDF2, pdfplumber, python-docx (text extraction)
- pydub, librosa (audio processing)
- openai, elevenlabs, google-cloud-texttospeech (TTS)
- pillow (image processing)
- feedgen (RSS generation)

### Пользовательские настройки
- Создан не-root пользователь `appuser`
- Работа в директории `/app`
- Открыт порт 8000
- Health check на `/health`

## 🚨 Важные замечания

1. **API ключи**: Не включайте API ключи в Docker образ. Используйте переменные окружения.

2. **Объем памяти**: Для работы с аудио может потребоваться больше памяти (рекомендуется 4GB+).

3. **Файлы**: Образ использует volume монтирование для хранения загруженных файлов и кэша.

4. **Порты**: Образ слушает порт 8000, но может быть изменен при необходимости.

## 🧪 Тестирование образа

После запуска проверьте работу:

```bash
# Проверка состояния контейнера
docker ps

# Проверка логов
docker logs ai-podcast-platform

# Проверка health check
curl http://localhost:8000/health
```

## 📁 Структура томов

- `/app/uploads` - загруженные файлы
- `/app/cache` - кэшированные данные

Эти директории должны быть смонтированы при запуске контейнера.