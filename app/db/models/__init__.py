"""Пакет с ORM-моделями SmartMonitor.

Импорт моделей нужен, чтобы SQLAlchemy зарегистрировала их в metadata
при инициализации базы данных.
"""

from app.db.models.product import Product

__all__ = ["Product"]
