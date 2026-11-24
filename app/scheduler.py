"""Фоновый планировщик задач приложения SmartMonitor.

Здесь описаны периодические задачи (например, проверка цен товаров),
которые запускаются в фоне, не блокируя обработку HTTP-запросов.
"""

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.core.logger import logger
from app.database import async_session_maker
from app.services import product_service

# Максимальное число одновременно проверяемых товаров
MAX_CONCURRENT_CHECKS = 5


async def _check_product(product_id: int, semaphore: asyncio.Semaphore) -> None:
    """Проверяет один товар в изолированной сессии БД."""
    async with semaphore:
        async with async_session_maker() as db:
            try:
                product = await product_service.check_and_update_price(db, product_id)
                if product is None:
                    return

                logger.info("Товар успешно проверен", product_id=product.id)
            except Exception:
                logger.exception("Ошибка при проверке товара", product_id=product_id)


async def check_all_prices() -> None:
    """
    Фоновая задача: проверяет цены для всех товаров.
    Вызывается планировщиком каждые N минут.
    """
    async with async_session_maker() as db:
        product_ids = await product_service.get_product_ids(db)

    logger.info("Запущена фоновая проверка цен", products_count=len(product_ids))

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CHECKS)
    await asyncio.gather(
        *(_check_product(product_id, semaphore) for product_id in product_ids)
    )

    logger.info("Фоновая проверка цен завершена")


def start_scheduler() -> AsyncIOScheduler:
    """Создает и запускает планировщик задач."""
    scheduler = AsyncIOScheduler()

    # Задача выполняется каждые N минут (интервал задается в настройках)
    scheduler.add_job(
        check_all_prices,
        trigger=IntervalTrigger(minutes=settings.CHECK_INTERVAL_MINUTES),
        id="check_prices_job",
        name="Проверка цен товаров",
        replace_existing=True,
        max_instances=1,  # Не запускать новую задачу, если предыдущая еще работает
    )

    scheduler.start()
    logger.info(
        "Планировщик задач запущен",
        interval_minutes=settings.CHECK_INTERVAL_MINUTES,
    )
    return scheduler
