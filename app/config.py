"""Настройки приложения SmartMonitor.

Значения читаются из переменных окружения, а также из файла .env
(если он существует в корне проекта).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Название сервиса (используется в заголовке API и ответах)
    APP_NAME: str = "SmartMonitor"
    # Режим отладки
    DEBUG: bool = True
    # Префикс для маршрутов версии v1
    API_V1_PREFIX: str = "/api/v1"
    # DSN для подключения к базе данных (асинхронный SQLite)
    DATABASE_URL: str = "sqlite+aiosqlite:///./smartmonitor.db"


# Единый объект настроек для всего приложения
settings = Settings()
