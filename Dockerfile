FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание директории для медиа файлов
RUN mkdir -p /app/media

# Применение миграций и запуск сервера
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000

