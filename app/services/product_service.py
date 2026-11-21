"""Сервисный слой для работы с товарами (Product).

Здесь сосредоточена вся бизнес-логика: доступ к БД, парсинг цены и т.д.
API-эндпоинты лишь вызывают функции сервиса и обрабатывают HTTP-ответы.
"""

import random

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.db.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def create_product(db: AsyncSession, product_in: ProductCreate) -> Product:
    """Создает новый товар в БД."""
    product = Product(**product_in.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def get_product(db: AsyncSession, product_id: int) -> Product | None:
    """Получает товар по ID."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()


async def get_all_products(db: AsyncSession) -> list[Product]:
    """Получает список всех товаров."""
    result = await db.execute(select(Product))
    return result.scalars().all()


async def update_product(
    db: AsyncSession, product_id: int, product_in: ProductUpdate
) -> Product | None:
    """Обновляет данные товара."""
    db_product = await get_product(db, product_id)
    if not db_product:
        return None

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)

    await db.commit()
    await db.refresh(db_product)
    return db_product


async def delete_product(db: AsyncSession, product_id: int) -> bool:
    """Удаляет товар. Возвращает True если успешно, False если не найден."""
    db_product = await get_product(db, product_id)
    if not db_product:
        return False
    await db.delete(db_product)
    await db.commit()
    return True


async def check_and_update_price(db: AsyncSession, product_id: int) -> Product | None:
    """
    Асинхронно заходит на URL товара и обновляет current_price.
    ВНИМАНИЕ: Для учебных целей мы делаем упрощенный запрос через httpx.
    В реальном проекте с защитой (Ozon/WB) здесь будет Playwright.
    """
    product = await get_product(db, product_id)
    if not product:
        return None

    try:
        # Делаем асинхронный HTTP-запрос
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(product.url, follow_redirects=True)
            response.raise_for_status()

            # УЧЕБНАЯ ЗАГЛУШКА: Поскольку Ozon блокирует простые запросы,
            # мы симулируем успешный парсинг, генерируя цену около target_price.
            # В будущем здесь будет BeautifulSoup или Playwright для реального парсинга.
            simulated_price = (
                product.target_price * random.uniform(0.9, 1.1)
                if product.target_price
                else 50000.0
            )

            product.current_price = round(simulated_price, 2)
            await db.commit()
            await db.refresh(product)

            # Логируем успешный запрос к сайту товара
            logger.info("Успешный запрос к сайту", product_id=product.id, url=product.url)

    except httpx.HTTPError as e:
        # Если сайт недоступен, логируем ошибку с контекстом товара
        logger.error(
            "Ошибка при проверке цены",
            product_id=product.id,
            url=product.url,
            error=str(e),
        )

    return product
