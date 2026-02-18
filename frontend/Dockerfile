# ============================================================
# Stage 1: Builder — сборка React приложения
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package.json package-lock.json* ./
RUN npm ci --frozen-lockfile

# Копируем исходный код
COPY . .

# Аргументы сборки (передаются через docker-compose)
ARG VITE_API_URL=http://localhost
ENV VITE_API_URL=$VITE_API_URL

# Собираем production build
RUN npm run build

# ============================================================
# Stage 2: Production — только статические файлы
# ============================================================
FROM nginx:alpine AS production

# Копируем собранные файлы
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx конфиг для SPA (React Router)
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ { \
        expires 30d; \
        add_header Cache-Control "public, immutable"; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
