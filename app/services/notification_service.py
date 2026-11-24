"""Сервис уведомлений SmartMonitor.

Отправка уведомлений о падении цены во внешние мессенджеры.
Реализован паттерн Strategy: конкретная реализация выбирается
через настройку NOTIFICATION_BACKEND.
"""

from typing import Protocol

import httpx

from app.config import settings
from app.core.logger import logger
from app.db.models.product import Product


class NotificationSender(Protocol):
    """Общий интерфейс отправителя уведомлений."""

    async def send_alert(self, product: Product) -> bool:
        """Отправляет уведомление о товаре. Возвращает True при успехе."""
        ...


class MockNotificationSender:
    """Имитация отправки уведомления (используется по умолчанию)."""

    async def send_alert(self, product: Product) -> bool:
        logger.info(
            "[MAX API MOCK] Имитация отправки уведомления о падении цены",
            product_id=product.id,
            product_name=product.name,
            current_price=product.current_price,
            target_price=product.target_price,
            url=product.url,
        )
        return True


class MaxNotificationSender:
    """Отправка уведомления через реальный API MAX."""

    async def send_alert(self, product: Product) -> bool:
        text = (
            f"Цена упала: {product.name}\n"
            f"Текущая цена: {product.current_price}\n"
            f"Целевая цена: {product.target_price}\n"
            f"{product.url}"
        )
        payload = {"chat_id": settings.MAX_CHAT_ID, "text": text}
        headers = {"Authorization": f"Bearer {settings.MAX_API_TOKEN}"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{settings.MAX_API_URL}/messages/send",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(
                "Ошибка отправки уведомления в MAX",
                product_id=product.id,
                url=product.url,
                error=str(e),
            )
            return False

        logger.info(
            "Уведомление отправлено в MAX",
            product_id=product.id,
            product_name=product.name,
        )
        return True


def get_notification_sender() -> NotificationSender:
    """Возвращает отправителя, выбранного настройкой NOTIFICATION_BACKEND."""
    if settings.NOTIFICATION_BACKEND == "max":
        return MaxNotificationSender()
    return MockNotificationSender()
