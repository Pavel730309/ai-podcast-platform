#!/bin/bash
# ============================================================
# AI Podcast Platform — Скрипт деплоя на VPS
# Использование: bash deploy-vps.sh
# ============================================================

set -e  # Остановить при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ---- Конфигурация ----
APP_DIR="/opt/ai-podcast-platform"
REPO_URL="https://github.com/Pavel730309/ai-podcast-platform.git"
BRANCH="main"

echo ""
echo "=============================================="
echo "  AI Podcast Platform — Деплой на VPS"
echo "=============================================="
echo ""

# ---- 1. Проверка зависимостей ----
log_info "Проверка зависимостей..."

command -v docker >/dev/null 2>&1 || log_error "Docker не установлен. Установите: curl -fsSL https://get.docker.com | sh"
command -v docker-compose >/dev/null 2>&1 || {
    # Проверяем docker compose (v2)
    docker compose version >/dev/null 2>&1 || log_error "Docker Compose не установлен."
    DOCKER_COMPOSE="docker compose"
}
DOCKER_COMPOSE="${DOCKER_COMPOSE:-docker-compose}"

log_success "Docker и Docker Compose найдены"

# ---- 2. Создание директории приложения ----
log_info "Подготовка директории $APP_DIR..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# ---- 3. Клонирование или обновление репозитория ----
if [ -d ".git" ]; then
    log_info "Обновление репозитория..."
    git fetch origin
    git reset --hard origin/$BRANCH
    git pull origin $BRANCH
    log_success "Репозиторий обновлён"
else
    log_info "Клонирование репозитория..."
    git clone -b $BRANCH $REPO_URL .
    log_success "Репозиторий склонирован"
fi

# ---- 4. Проверка .env файла ----
if [ ! -f ".env" ]; then
    log_warn ".env файл не найден!"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_warn "Создан .env из .env.example"
        log_warn "ОБЯЗАТЕЛЬНО отредактируйте .env перед запуском:"
        log_warn "  nano $APP_DIR/.env"
        echo ""
        echo "Нажмите Enter после редактирования .env, или Ctrl+C для отмены..."
        read -r
    else
        log_error ".env.example не найден. Создайте .env вручную."
    fi
else
    log_success ".env файл найден"
fi

# ---- 5. Проверка обязательных переменных ----
log_info "Проверка обязательных переменных в .env..."

check_env_var() {
    local var_name=$1
    local var_value
    var_value=$(grep "^${var_name}=" .env | cut -d'=' -f2-)
    if [ -z "$var_value" ] || [ "$var_value" = "CHANGE_ME_STRONG_PASSWORD" ] || [ "$var_value" = "CHANGE_ME_GENERATE_STRONG_SECRET_KEY" ] || [ "$var_value" = "sk-..." ]; then
        log_warn "Переменная $var_name не задана или содержит placeholder!"
        return 1
    fi
    return 0
}

MISSING_VARS=0
check_env_var "POSTGRES_PASSWORD" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "SECRET_KEY" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "OPENAI_API_KEY" || MISSING_VARS=$((MISSING_VARS + 1))

if [ $MISSING_VARS -gt 0 ]; then
    log_warn "$MISSING_VARS обязательных переменных не заданы. Продолжить? (y/N)"
    read -r CONTINUE
    [ "$CONTINUE" = "y" ] || [ "$CONTINUE" = "Y" ] || log_error "Деплой отменён. Заполните .env файл."
fi

# ---- 6. Остановка старых контейнеров ----
log_info "Остановка старых контейнеров..."
$DOCKER_COMPOSE down --remove-orphans 2>/dev/null || true
log_success "Старые контейнеры остановлены"

# ---- 7. Сборка образов ----
log_info "Сборка Docker образов (это может занять несколько минут)..."
$DOCKER_COMPOSE build --no-cache
log_success "Образы собраны"

# ---- 8. Запуск базы данных и Redis ----
log_info "Запуск базы данных и Redis..."
$DOCKER_COMPOSE up -d db redis
log_info "Ожидание готовности базы данных (30 сек)..."
sleep 30
log_success "База данных и Redis запущены"

# ---- 9. Применение миграций ----
log_info "Применение миграций базы данных..."
$DOCKER_COMPOSE run --rm backend alembic upgrade head
log_success "Миграции применены"

# ---- 10. Запуск всех сервисов ----
log_info "Запуск всех сервисов..."
$DOCKER_COMPOSE up -d
log_success "Все сервисы запущены"

# ---- 11. Ожидание и проверка ----
log_info "Ожидание запуска сервисов (60 сек)..."
sleep 60

log_info "Проверка статуса сервисов..."
$DOCKER_COMPOSE ps

# Проверка health check
log_info "Проверка health check..."
if curl -sf http://localhost/health > /dev/null 2>&1; then
    log_success "Health check прошёл успешно!"
else
    log_warn "Health check не прошёл. Проверьте логи:"
    log_warn "  $DOCKER_COMPOSE logs --tail=50 backend"
    log_warn "  $DOCKER_COMPOSE logs --tail=50 nginx"
fi

# ---- 12. Итог ----
echo ""
echo "=============================================="
echo -e "${GREEN}  Деплой завершён!${NC}"
echo "=============================================="
echo ""

# Получаем IP сервера
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo -e "  Приложение доступно по адресу: ${GREEN}http://$SERVER_IP${NC}"
echo -e "  API документация: ${GREEN}http://$SERVER_IP/docs${NC}"
echo ""
echo "  Полезные команды:"
echo "    Логи:          $DOCKER_COMPOSE logs -f"
echo "    Статус:        $DOCKER_COMPOSE ps"
echo "    Перезапуск:    $DOCKER_COMPOSE restart"
echo "    Остановка:     $DOCKER_COMPOSE down"
echo ""
