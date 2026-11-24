"""Сервисный слой для работы с товарами (Product).

Здесь сосредоточена вся бизнес-логика: доступ к БД, парсинг цены и т.д.
API-эндпоинты лишь вызывают функции сервиса и обрабатывают HTTP-ответы.
"""

import random
from decimal import ROUND_HALF_UP, Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.db.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.notification_service import get_notification_sender

# Переиспользуемый HTTP-клиент с базовым User-Agent
_http_client: httpx.AsyncClient | None = None

_PRICE_QUANT = Decimal("0.01")


def get_http_client() -> httpx.AsyncClient:
    """Возвращает единый (лениво созданный) HTTP-клиент приложения."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": "SmartMonitor/1.0 (+https://github.com/smartmonitor)"},
        )
    return _http_client


async def close_http_client() -> None:
    """Закрывает единый HTTP-клиент при остановке приложения."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
    _http_client = None


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
    return list(result.scalars().all())


async def get_product_ids(db: AsyncSession) -> list[int]:
    """Получает список ID всех товаров."""
    result = await db.execute(select(Product.id))
    return list(result.scalars().all())


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
    Асинхронно заходит на URL товара, обновляет current_price
    и при достижении target_price отправляет уведомление.
    ВНИМАНИЕ: Для учебных целей мы делаем упрощенный запрос через httpx.
    В реальном проекте с защитой (Ozon/WB) здесь будет Playwright.
    """
    product = await get_product(db, product_id)
    if not product:
        return None

    try:
        # Делаем асинхронный HTTP-запрос переиспользуемым клиентом
        client = get_http_client()
        response = await client.get(product.url)
        response.raise_for_status()

        # УЧЕБНАЯ ЗАГЛУШКА: Поскольку Ozon блокирует простые запросы,
        # мы симулируем успешный парсинг, генерируя цену около target_price.
        # В будущем здесь будет BeautifulSoup или Playwright для реального парсинга.
        if product.target_price is not None:
            factor = Decimal(str(random.uniform(0.9, 1.1)))
            simulated_price = product.target_price * factor
        else:
            simulated_price = Decimal("50000.00")

        product.current_price = simulated_price.quantize(
            _PRICE_QUANT, rounding=ROUND_HALF_UP
        )

        # Логика уведомления: шлем один раз при достижении цели,
        # сбрасываем флаг, если цена снова выросла выше target_price.
        if product.target_price is not None:
            if product.current_price <= product.target_price:
                if not product.is_notified:
                    product.is_notified = True
                    await get_notification_sender().send_alert(product)
            elif product.is_notified:
                product.is_notified = False

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
