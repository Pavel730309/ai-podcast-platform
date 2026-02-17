# 🚀 Инструкция по загрузке проекта на GitHub

## Шаг 1: Создание репозитория на GitHub

1. Перейдите на сайт [GitHub](https://github.com/)
2. Войдите в свой аккаунт
3. Нажмите кнопку "New repository" (или перейдите по ссылке: https://github.com/new)
4. Заполните поля:
   - **Repository name**: `ai-podcast-platform`
   - **Description**: `AI Podcast Platform - создание аудио-подкастов из текстовых материалов`
   - **Public**: ✓ (публичный репозиторий)
   - **Initialize this repository with**: ✗ (не добавлять README, .gitignore и т.д.)
5. Нажмите "Create repository"

## Шаг 2: Локальная настройка Git

1. Откройте терминал в папке проекта
2. Инициализируйте локальный репозиторий:
```bash
git init
```

3. Добавьте все файлы в коммит:
```bash
git add .
```

4. Сделайте первый коммит:
```bash
git commit -m "Initial commit of AI Podcast Platform"
```

5. Добавьте удаленный репозиторий:
```bash
git remote add origin https://github.com/Pavel-Perm/ai-podcast-platform.git
```

## Шаг 3: Загрузка проекта на GitHub

1. Загрузите код на GitHub:
```bash
git push -u origin main
```

2. Если возникнут проблемы с аутентификацией, используйте:
```bash
git push -u origin main --force-with-lease
```

## Шаг 4: Проверка

1. Перейдите на страницу вашего репозитория: https://github.com/Pavel-Perm/ai-podcast-platform
2. Убедитесь, что все файлы загружены корректно
3. Проверьте, что README.md, .gitignore и другие файлы присутствуют

## 📝 Дополнительные рекомендации

- Убедитесь, что в `.gitignore` правильно исключены временные и служебные файлы
- Проверьте, что в `.env.example` нет чувствительных данных
- Убедитесь, что все зависимости указаны в `requirements.txt`

## 🛡️ Безопасность

- Не добавляйте в репозиторий файлы с API ключами
- Используйте `.env.example` для примера конфигурации
- Рассмотрите возможность использования GitHub Secrets для CI/CD

## 🔄 Дальнейшие действия

После успешной загрузки проекта на GitHub можно продолжить:
1. Настройку Docker образа
2. Загрузку образа в Docker Hub
3. Подготовку VPS для размещения
4. Деплой на сервере