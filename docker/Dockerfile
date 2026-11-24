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

# gosu — для сброса привилегий root -> appuser в entrypoint (доступ к примонтированному ./data)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# Копируем исходный код приложения
COPY app/ ./app/
COPY scripts/ ./scripts/

# Копируем файлы Alembic для авто-миграций при старте контейнера
COPY alembic.ini ./alembic.ini
COPY alembic/ ./alembic/

# Каталог для файла SQLite (на случай запуска без монтирования volume)
RUN mkdir -p /app/data

# Создаём системного непривилегированного пользователя и передаём ему права на /app
RUN adduser --system --group --no-create-home appuser \
    && chown -R appuser:appuser /app

# Entrypoint: при старте от root корректирует владельца смонтированного /app/data
# и сбрасывает привилегии до appuser (иначе запись в volume с хоста может быть недоступна)
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Порт, который слушает приложение (для документации образа и оркестраторов)
EXPOSE 8000

# Команда запуска: сначала накатываем миграции, затем стартуем сервер
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
