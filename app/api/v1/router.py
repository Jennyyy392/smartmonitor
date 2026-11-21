"""Маршруты API версии v1."""

from fastapi import APIRouter

from app.api.v1.endpoints import products
from app.config import settings

# Основной роутер для версии v1
router = APIRouter()

# Подключаем эндпоинты товаров
router.include_router(products.router, prefix="/products", tags=["products"])


@router.get("/health", tags=["health"], summary="Проверка работоспособности")
async def health() -> dict[str, str]:
    """Возвращает статус сервиса и его название."""
    return {"status": "ok", "service": settings.APP_NAME}
