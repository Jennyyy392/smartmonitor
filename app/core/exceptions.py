"""Глобальные обработчики исключений приложения SmartMonitor."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.logger import logger


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Глобальный обработчик для всех необработанных исключений.
    Логирует ошибку с полным стек-трейсом и возвращает клиенту безопасный JSON.
    """
    # Логируем ошибку с полным traceback (уровень ERROR)
    logger.exception(
        "Необработанное исключение в приложении",
        method=request.method,
        url=str(request.url),
        client_host=request.client.host if request.client else "unknown",
        error_type=type(exc).__name__,
        error_message=str(exc),
    )

    # Возвращаем безопасный ответ клиенту (без утечки traceback)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal Server Error. Пожалуйста, попробуйте позже или обратитесь в поддержку.",
            "error_type": type(exc).__name__,
        },
    )
