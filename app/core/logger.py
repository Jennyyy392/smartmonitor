"""Настройка структурированного логирования (structlog) для SmartMonitor.

Логи ведут себя по-разному в зависимости от режима settings.DEBUG:
- DEBUG=True  -> цветные человекочитаемые логи в консоли (для разработки).
- DEBUG=False -> строгий JSON-формат (для продакшена и систем сбора логов).
"""

import sys

import structlog

from app.config import settings


def setup_logging() -> None:
    """Настраивает structlog в зависимости от окружения."""
    if settings.DEBUG:
        # Разработка: цветные, читаемые логи
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # Продакшен: строгий JSON для систем сбора логов
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


# Создаем глобальный экземпляр логгера для импорта в других модулях
logger = structlog.get_logger()
