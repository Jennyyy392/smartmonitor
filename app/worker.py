"""Точка входа отдельного процесса-воркера SmartMonitor.

Запускает только планировщик фоновых задач, без HTTP-сервера.
Позволяет масштабировать API на несколько воркеров без дублирования фоновых
задач: сам API запускается с ENABLE_SCHEDULER=false.

Запуск: python -m app.worker
"""

import asyncio
import signal

from app.config import settings
from app.core.http import close_http_client
from app.core.logger import logger, setup_logging
from app.scheduler import start_scheduler


async def main() -> None:
    """Запускает планировщик и работает до получения сигнала завершения."""
    setup_logging()
    logger.info("Воркер запускается", debug_mode=settings.DEBUG)

    scheduler = start_scheduler()
    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            # Windows не поддерживает add_signal_handler; полагаемся на KeyboardInterrupt
            pass

    try:
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        scheduler.shutdown()
        logger.info("Планировщик остановлен")
        await close_http_client()


if __name__ == "__main__":
    asyncio.run(main())
