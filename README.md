# SmartMonitor
![Build Status](https://img.shields.io/github/actions/workflow/status/Jennyyy392/smartmonitor/ci.yml?branch=main&label=build&style=for-the-badge)

**SmartMonitor** — учебно-боевой проект мониторинга цен. Сервис отслеживает
изменение цен на товары и помогает вовремя замечать выгодные предложения.

На текущем этапе реализован минимальный рабочий каркас: FastAPI-приложение
с проверкой работоспособности (health-check) и базовой конфигурацией.

## Стек

- Python 3.12
- FastAPI
- Pydantic / pydantic-settings

## Создание виртуального окружения (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Установка зависимостей

```powershell
pip install -r requirements.txt
```

## Запуск сервера

```powershell
uvicorn app.main:app --reload
```

## 🐳 Запуск через Docker

Сборка образа:

```powershell
docker-compose -f docker/docker-compose.yml build
```

Запуск контейнера в фоне:

```powershell
docker-compose -f docker/docker-compose.yml up -d
```

Просмотр логов:

```powershell
docker-compose -f docker/docker-compose.yml logs -f
```

## Документация (Swagger)

После запуска откройте в браузере:

- http://127.0.0.1:8000 — корневой эндпоинт
- http://127.0.0.1:8000/docs — интерактивная документация Swagger
- http://127.0.0.1:8000/api/v1/health — проверка работоспособности

## Структура проекта

```
smartmonitor/
├── app/
│   ├── main.py          # точка входа приложения
│   ├── config.py        # настройки (pydantic-settings)
│   ├── api/v1/router.py # маршруты версии v1
│   ├── core/            # общая логика
│   ├── db/              # слой базы данных
│   ├── schemas/         # Pydantic-схемы
│   └── services/        # бизнес-логика
├── tests/               # тесты
├── scripts/             # вспомогательные скрипты
└── docker/              # файлы для Docker
```
