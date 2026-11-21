"""Базовый класс для всех ORM-моделей SmartMonitor."""

from sqlalchemy.orm import declarative_base

# Базовый класс для всех моделей: от него наследуются таблицы БД
Base = declarative_base()
