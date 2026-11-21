"""Конфигурация окружения Alembic для асинхронного SQLAlchemy (aiosqlite).

Alembic работает синхронно, поэтому асинхронный движок создаётся вручную
через async_engine_from_config, а сами миграции выполняются внутри
соединения с помощью connection.run_sync().
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.config import settings
from app.db import models  # noqa: F401  # Импорт нужен для регистрации моделей
from app.db.base import Base

# Объект Config, дающий доступ к значениям из alembic.ini
config = context.config

# Настройка логирования из alembic.ini (секции [loggers] и т.д.)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные всех моделей — источник данных для режима --autogenerate
target_metadata = Base.metadata


def get_url() -> str:
    """Возвращает URL базы данных из настроек приложения."""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Запускает миграции в 'offline' режиме.

    В этом режиме соединение с базой не создаётся: Alembic только
    формирует SQL-скрипт по заданному URL.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполняет миграции в рамках уже открытого синхронного соединения."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Создаёт асинхронный движок и выполняет миграции через него.

    Alembic внутри работает синхронно, поэтому используется
    connection.run_sync(), который выполняет синхронную функцию
    do_run_migrations в контексте асинхронного соединения.
    """
    # Берём секцию из alembic.ini и подменяем URL на актуальный из настроек
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запускает миграции в 'online' режиме через asyncio."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
