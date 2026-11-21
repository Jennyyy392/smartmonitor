"""Точка входа приложения SmartMonitor."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.config import settings
from app.core.exceptions import global_exception_handler
from app.core.logger import logger, setup_logging
from app.database import init_db
from app.scheduler import start_scheduler

# Ссылка на запущенный планировщик задач (доступна на уровне модуля)
scheduler_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Жизненный цикл приложения: инициализация БД и запуск планировщика."""
    global scheduler_instance

    # Настраиваем логирование в самом начале запуска приложения
    setup_logging()
    logger.info("Приложение запускается", debug_mode=settings.DEBUG)

    # Создаём таблицы в базе данных при запуске приложения
    await init_db()

    # Код, который выполняется при ЗАПУСКЕ приложения
    scheduler_instance = start_scheduler()

    yield  # Здесь работает приложение

    # Код, который выполняется при ОСТАНОВКЕ приложения
    if scheduler_instance:
        scheduler_instance.shutdown()
        logger.info("Планировщик остановлен")


# Создание приложения FastAPI
app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Регистрация глобального обработчика всех необработанных исключений
app.add_exception_handler(Exception, global_exception_handler)

# Подключение маршрутов v1 с префиксом из настроек
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"], summary="Корневой маршрут")
async def root() -> dict[str, str]:
    """Возвращает приветственное сообщение и ссылку на документацию."""
    return {"message": "SmartMonitor API is running", "docs": "/docs"}
