"""Подключение к базе данных в асинхронном режиме (SQLAlchemy 2.0)."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base

# Импорт моделей нужен, чтобы они зарегистрировались в Base.metadata до create_all
from app.db.models import Product  # noqa: F401

# Асинхронный движок базы данных
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

# Фабрика асинхронных сессий, привязанная к движку
async_session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Отдаёт сессию БД для dependency injection в FastAPI.

    Сессия автоматически закрывается после завершения запроса.
    """
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Создаёт таблицы в базе данных при старте приложения."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
