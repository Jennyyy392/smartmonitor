# 🚀 SmartMonitor

[![Build Status](https://img.shields.io/github/actions/workflow/status/Jennyyy392/smartmonitor/ci.yml?branch=main&label=build&style=for-the-badge)](https://github.com/Jennyyy392/smartmonitor/actions/workflows/ci.yml?query=branch%3Amain)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**SmartMonitor** — это асинхронный микросервис для мониторинга цен на товары. Сервис отслеживает изменения цен по заданным URL, сравнивает их с целевой ценой и отправляет уведомления при достижении цели.

Проект разработан с соблюдением лучших практик enterprise-разработки: чистая архитектура (Service Layer), асинхронная работа с БД, структурированное логирование, миграции и автоматизированный CI/CD.

## 🏗 Архитектура проекта

```mermaid
graph TD
    Client[Клиент / Swagger UI] -->|HTTP REST| API[FastAPI Application]
    API -->|Dependency Injection| Service[Service Layer]
    Service -->|Async SQLAlchemy| DB[(SQLite / Alembic Migrations)]
    Service -->|HTTPX| External[Внешние сайты / Парсинг]
    Scheduler[APScheduler Background Worker] -->|Trigger| Service
    Service -->|Structlog JSON/Console| Logs[Система логирования]
```

Поток обработки запроса:

1. **HTTP-слой** (`app/api`) принимает запрос, валидирует данные через Pydantic-схемы и делегирует работу сервису.
2. **Сервисный слой** (`app/services`) содержит бизнес-логику и обращается к БД и внешним сайтам.
3. **Слой данных** (`app/db`) описывает ORM-модели, а миграции управляются через Alembic.
4. **Фоновый воркер** (`APScheduler`) периодически запускает проверку цен, не блокируя обработку HTTP-запросов.

## 🛠 Технологический стек и обоснование выбора

- **FastAPI**: Высокая производительность, нативная поддержка async/await и автоматическая генерация Swagger-документации.
- **SQLAlchemy 2.0 (Async) + aiosqlite**: Современный асинхронный ORM для неблокирующей работы с базой данных.
- **Alembic**: Версионирование и управление миграциями схемы базы данных (безопасные upgrade/downgrade).
- **Pydantic v2**: Строгая валидация входящих и исходящих данных.
- **APScheduler**: Надежный планировщик фоновых задач для периодической проверки цен.
- **Structlog**: Структурированное логирование (цветной вывод в dev, JSON в prod) для удобной интеграции с системами мониторинга (ELK, Grafana Loki).
- **Pytest + HTTPX**: Изолированное модульное и интеграционное тестирование API с использованием in-memory SQLite.
- **Ruff**: Молниеносный линтер и форматтер кода для поддержания чистоты и единого стиля.

## 🚀 Быстрый старт

### Вариант 1: Docker (Рекомендуется)

Самый быстрый способ развернуть приложение со всеми зависимостями:

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Jennyyy392/smartmonitor.git
cd smartmonitor

# 2. Создать файл окружения (при необходимости)
echo "DEBUG=False" > .env

# 3. Собрать и запустить контейнер
docker-compose -f docker/docker-compose.yml up -d --build
```

Приложение будет доступно по адресу: <http://localhost:8000/docs>

### Вариант 2: Локальный запуск

```powershell
# 1. Создать и активировать виртуальное окружение
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Применить миграции к базе данных
alembic upgrade head

# 4. Запустить сервер разработки
uvicorn app.main:app --reload
```

## 🗄 Миграции базы данных (Alembic)

Схема БД управляется исключительно через миграции — ручное изменение таблиц не требуется (и не рекомендуется).

```bash
# Применить все миграции до последней ревизии
alembic upgrade head

# Откатить последнюю миграцию
alembic downgrade -1

# Создать новую миграцию по изменениям ORM-моделей
alembic revision --autogenerate -m "add new field"

# Посмотреть текущую ревизию
alembic current
```

## 📖 API Reference

После запуска интерактивная документация доступна по адресам:

- <http://127.0.0.1:8000/docs> — Swagger UI
- <http://127.0.0.1:8000/redoc> — ReDoc

| Метод    | Эндпоинт                             | Описание                                   |
| -------- | ------------------------------------ | ------------------------------------------ |
| `GET`    | `/`                                  | Корневой маршрут, статус сервиса           |
| `GET`    | `/api/v1/health`                     | Проверка работоспособности (health-check)  |
| `POST`   | `/api/v1/products/`                  | Создать товар для отслеживания             |
| `GET`    | `/api/v1/products/`                  | Получить список всех товаров               |
| `GET`    | `/api/v1/products/{id}`              | Получить товар по ID                       |
| `PATCH`  | `/api/v1/products/{id}`              | Частично обновить товар (основной)         |
| `PUT`    | `/api/v1/products/{id}`              | Частично обновить товар (устаревший alias) |
| `DELETE` | `/api/v1/products/{id}`              | Удалить товар                              |
| `POST`   | `/api/v1/products/{id}/check-price`  | Запустить проверку цены вручную            |

### Пример запроса

```bash
curl -X POST http://127.0.0.1:8000/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Наушники Sony WH-1000XM5",
    "url": "https://www.ozon.ru/product/...",
    "target_price": 25000.0
  }'
```

## ⚙️ Конфигурация

Настройки читаются из переменных окружения и файла `.env` (см. `app/config.py`):

| Переменная        | Значение по умолчанию                          | Описание                              |
| ----------------- | ---------------------------------------------- | ------------------------------------- |
| `APP_NAME`        | `SmartMonitor`                                 | Название сервиса                      |
| `DEBUG`           | `True`                                         | Режим отладки (влияет на логи и echo) |
| `API_V1_PREFIX`   | `/api/v1`                                      | Префикс маршрутов v1                  |
| `DATABASE_URL`    | `sqlite+aiosqlite:///./smartmonitor.db`        | DSN подключения к базе данных         |

## 🧩 Ключевые инженерные решения

### Асинхронность из коробки

Все слои приложения асинхронны: FastAPI-эндпоинты, сервисы, SQLAlchemy-сессии (`AsyncSession`) и HTTP-запросы через `httpx.AsyncClient`. Это позволяет обслуживать множество запросов без блокировки event loop, а фоновый воркер работает в том же процессе, не мешая обработке HTTP-трафика.

### Глобальная обработка ошибок

В `app/core/exceptions.py` зарегистрирован глобальный обработчик необработанных исключений. Он логирует ошибку с полным стек-трейсом и контекстом запроса, а клиенту возвращает безопасный JSON без утечки внутренних деталей реализации.

### Структурированное логирование (structlog)

Логирование настраивается в зависимости от окружения: в режиме `DEBUG=True` — цветной человекочитаемый вывод для разработки, в `DEBUG=False` — строгий JSON с ISO-таймстампами для продакшена и систем сбора логов (ELK, Grafana Loki). Все логи обогащаются контекстом (например, `product_id`, `url`).

### Фоновые задачи (APScheduler)

Планировщик запускается в `lifespan`-контексте приложения и корректно останавливается при выключении. Задача `check_all_prices` выполняется каждые 5 минут, имеет защиту `max_instances=1` (новая задача не стартует, пока работает предыдущая) и изолированную обработку ошибок по каждому товару.

## 🧪 Тестирование

Тесты используют in-memory SQLite и dependency override для полной изоляции от рабочей базы данных.

```bash
# Запустить все тесты
pytest -v

# Проверить код линтером
ruff check .

# Автоматически исправить замечания линтера
ruff check . --fix

# Форматирование кода
ruff format .
```

## 🔄 CI/CD

Проект использует GitHub Actions (`.github/workflows/ci.yml`). Пайплайн запускается при каждом push и pull request в ветку `main` и выполняет:

1. Установку Python 3.12.
2. Кэширование pip-зависимостей для ускорения сборок.
3. Линтинг кода через Ruff.
4. Запуск тестов через Pytest.

Статус сборки отображается бейджем в начале этого файла.

## 📁 Структура проекта

```
smartmonitor/
├── app/
│   ├── main.py              # точка входа, lifespan, регистрация обработчиков
│   ├── config.py            # настройки (pydantic-settings)
│   ├── database.py          # асинхронный движок и сессии SQLAlchemy
│   ├── scheduler.py         # фоновый планировщик проверки цен
│   ├── api/v1/              # HTTP-слой: роутеры и эндпоинты
│   ├── core/                # логирование и глобальная обработка ошибок
│   ├── db/                  # ORM-модели и declarative base
│   ├── schemas/             # Pydantic-схемы (валидация)
│   └── services/            # бизнес-логика (Service Layer)
├── alembic/                 # миграции базы данных
├── docker/                  # Dockerfile и docker-compose
├── tests/                   # pytest-тесты (unit / integration)
├── scripts/                 # вспомогательные скрипты
└── .github/workflows/       # CI/CD пайплайн
```

## 📄 Лицензия

Проект распространяется под лицензией **MIT**.
