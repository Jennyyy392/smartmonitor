"""Сервис уведомлений SmartMonitor.

Здесь сосредоточена логика отправки уведомлений о падении цены
во внешние мессенджеры (сейчас — MAX в режиме Mock).
"""

# httpx понадобится для реального API MAX (код ниже), пока закомментирован.
import httpx  # noqa: F401

from app.core.logger import logger
from app.db.models.product import Product


async def send_max_notification(product: Product) -> bool:
    """
    Отправляет уведомление в мессенджер MAX о падении цены.
    Сейчас это Mock (имитация), но структура полностью готова для реального API.
    """
    if product.current_price is None or product.target_price is None:
        return False

    if product.current_price <= product.target_price:
        # --- ПРОДАКШЕН КОД (раскомментировать при наличии API ключа MAX) ---
        # max_api_url = "`https://api.max-messenger.ru/v1/messages/send`"
        # headers = {"Authorization": "Bearer YOUR_MAX_API_KEY"}
        # payload = {"chat_id": "YOUR_CHAT_ID", "text": f"Цена упала: {product.name}"}
        # ... (логика httpx запроса) ...
        # -------------------------------------------------------------------

        # --- MOCK ДЛЯ ТЕСТИРОВАНИЯ АРХИТЕКТУРЫ ---
        logger.info(
            "[MAX API MOCK] Имитация отправки уведомления о падении цены",
            product_id=product.id,
            product_name=product.name,
            current_price=product.current_price,
            target_price=product.target_price,
            url=product.url
        )
        return True

    return False
