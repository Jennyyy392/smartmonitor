"""Настройки приложения SmartMonitor.

Значения читаются из переменных окружения, а также из файла .env
(если он существует в корне проекта).
"""

from typing import Literal

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
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/smartmonitor.db"
    # Интервал фоновой проверки цен (в минутах)
    CHECK_INTERVAL_MINUTES: int = 5
    # Бэкенд уведомлений: "mock" — имитация, "max" — реальный API MAX
    NOTIFICATION_BACKEND: Literal["mock", "max"] = "mock"
    # Параметры API MAX (используются при NOTIFICATION_BACKEND="max")
    MAX_API_URL: str = "https://api.max-messenger.ru/v1"
    MAX_API_TOKEN: str = ""
    MAX_CHAT_ID: str = ""


# Единый объект настроек для всего приложения
settings = Settings()
