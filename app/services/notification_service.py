"""Сервис уведомлений SmartMonitor.

Здесь сосредоточена логика отправки уведомлений о падении цены
во внешние мессенджеры (сейчас — MAX в режиме Mock).
"""

# httpx понадобится для реального API MAX (код ниже), пока закомментирован.
import httpx  # noqa: F401

from app.db.models.product import Product


async def send_max_notification(product: Product) -> bool:
    """
    Отправляет уведомление в мессенджер MAX о падении цены.
    Сейчас это Mock (имитация), но структура полностью готова для реального API.
    """
    if product.current_price is None or product.target_price is None:
        return False

    if product.current_price <= product.target_price:
        message = (
            f"🔥 ЦЕНА УПАЛА! 🔥\n"
            f"Товар: {product.name}\n"
            f"Текущая цена: {product.current_price} ₽\n"
            f"Целевая цена: {product.target_price} ₽\n"
            f"Ссылка: {product.url}"
        )

        # --- ПРОДАКШЕН КОД (раскомментировать при наличии API ключа MAX) ---
        # max_api_url = "https://api.max-messenger.ru/v1/messages/send"
        # headers = {"Authorization": "Bearer YOUR_MAX_API_KEY"}
        # payload = {"chat_id": "YOUR_CHAT_ID", "text": message}
        #
        # try:
        #     async with httpx.AsyncClient() as client:
        #         response = await client.post(max_api_url, json=payload, headers=headers)
        #         response.raise_for_status()
        #     return True
        # except httpx.HTTPError as e:
        #     print(f"❌ Ошибка отправки в MAX: {e}")
        #     return False
        # -------------------------------------------------------------------

        # --- MOCK ДЛЯ ТЕСТИРОВАНИЯ АРХИТЕКТУРЫ ---
        print("\n" + "=" * 50)
        print("📨 [MAX API MOCK] Имитация отправки уведомления:")
        print(message)
        print("=" * 50 + "\n")
        return True

    return False
