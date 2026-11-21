"""Общие фикстуры для всех тестов SmartMonitor.

Здесь описаны настройки окружения pytest: тестовая БД и HTTP-клиент.
Благодаря фикстурам каждый тест получает чистую изолированную базу данных,
а основная рабочая smartmonitor.db не затрагивается.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.db.base import Base
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Создает временную тестовую БД для каждого теста."""
    # Используем in-memory SQLite для тестов (быстро и изолированно)
    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Создаем все таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаем сессию
    test_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with test_session_maker() as session:
        yield session

    # Удаляем все таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession):
    """Создает тестовый HTTP-клиент с подменой БД на тестовую."""

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
