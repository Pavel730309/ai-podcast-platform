# ============================================================
# Stage 1: Builder — устанавливаем зависимости
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Системные зависимости для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем в отдельную директорию
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================================
# Stage 2: Production — минимальный образ
# ============================================================
FROM python:3.11-slim AS production

WORKDIR /app

# Только runtime зависимости (без gcc и build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libsndfile1 \
    libsox-fmt-mp3 \
    sox \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем установленные Python-пакеты из builder
COPY --from=builder /install /usr/local

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Создаём непривилегированного пользователя
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Копируем код приложения
COPY --chown=appuser:appgroup . .

# Создаём директории для файлов
RUN mkdir -p /app/uploads /app/cache /app/logs && \
    chown -R appuser:appgroup /app/uploads /app/cache /app/logs

# Переключаемся на непривилегированного пользователя
USER appuser

# Открываем порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--loop", "uvloop"]
