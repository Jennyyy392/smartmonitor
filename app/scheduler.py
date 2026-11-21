"""Фоновый планировщик задач приложения SmartMonitor.

Здесь описаны периодические задачи (например, проверка цен товаров),
которые запускаются в фоне, не блокируя обработку HTTP-запросов.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from app.database import async_session_maker
from app.db.models.product import Product
from app.services import product_service
from app.services.notification_service import send_max_notification


async def check_all_prices() -> None:
    """
    Фоновая задача: проверяет цены для всех товаров.
    Вызывается планировщиком каждые N минут.
    """
    async with async_session_maker() as db:
        # Получаем все товары из БД
        result = await db.execute(select(Product))
        products = result.scalars().all()

        print(f"🔄 Запущена проверка цен для {len(products)} товаров...")

        for product in products:
            try:
                await product_service.check_and_update_price(db, product.id)
                print(f"✅ Проверен товар: {product.name} (ID: {product.id})")

                # Проверяем, упала ли цена до целевой или ниже
                if product.current_price is not None and product.target_price is not None:
                    if product.current_price <= product.target_price:
                        await send_max_notification(product)
            except Exception as e:
                print(f"❌ Ошибка при проверке {product.name}: {e}")

        print("🏁 Проверка завершена")


def start_scheduler() -> AsyncIOScheduler:
    """Создает и запускает планировщик задач."""
    scheduler = AsyncIOScheduler()

    # Задача выполняется каждые 5 минут (для тестов можно поставить 1 минуту)
    scheduler.add_job(
        check_all_prices,
        trigger=IntervalTrigger(minutes=5),
        id="check_prices_job",
        name="Проверка цен товаров",
        replace_existing=True,
        max_instances=1,  # Не запускать новую задачу, если предыдущая еще работает
    )

    scheduler.start()
    print("📅 Планировщик задач запущен. Проверка цен каждые 5 минут.")
    return scheduler
