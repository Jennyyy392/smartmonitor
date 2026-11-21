"""ORM-модель товара SmartMonitor."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.base import Base


class Product(Base):
    """Товар, цену которого отслеживает система.

    Поля:
        id: первичный ключ записи.
        name: название товара.
        url: уникальная ссылка на страницу товара в магазине.
        current_price: текущая цена товара (заполняется при парсинге).
        target_price: желаемая цена, при достижении которой отправляется уведомление.
        created_at: дата и время создания записи (UTC).
        updated_at: дата и время последнего обновления записи (UTC).
    """

    __tablename__ = "products"

    id: Column[int] = Column(Integer, primary_key=True, index=True)
    name: Column[str] = Column(String, nullable=False)
    url: Column[str] = Column(String, unique=True, index=True, nullable=False)
    current_price: Column[float | None] = Column(Float, nullable=True)
    target_price: Column[float | None] = Column(Float, nullable=True)
    created_at: Column[datetime] = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Column[datetime] = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
