"""Общий HTTP-клиент приложения.

Единый переиспользуемый httpx.AsyncClient для всех сервисов,
чтобы не создавать соединение на каждый запрос.
"""

import httpx

_http_client: httpx.AsyncClient | None = None


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