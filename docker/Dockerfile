# Базовый образ: облегчённая версия Python 3.12 (slim)
FROM python:3.12-slim

# Переменные окружения:
# PYTHONDONTWRITEBYTECODE — не создавать .pyc-файлы внутри контейнера
# PYTHONUNBUFFERED — выводить логи сразу, без буферизации
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочий каталог внутри контейнера
WORKDIR /app

# Сначала копируем только список зависимостей,
# чтобы Docker кэшировал слой установки пакетов
COPY requirements.txt .

# Установка зависимостей без кэша pip (уменьшает размер образа)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY app/ ./app/
COPY scripts/ ./scripts/

# Команда запуска сервера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
