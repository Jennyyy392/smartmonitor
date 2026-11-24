"""Pydantic-схемы для товара SmartMonitor."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ProductBase(BaseModel):
    """Базовые поля товара, общие для создания и ответа."""

    name: str = Field(..., min_length=2, max_length=100, description="Название товара")
    url: str = Field(..., description="Ссылка на товар")
    target_price: Decimal | None = Field(
        None, description="Желаемая цена для уведомления"
    )

    @field_serializer("target_price", when_used="json")
    def _serialize_target_price(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class ProductCreate(ProductBase):
    """Схема для создания нового товара."""

    pass


class ProductUpdate(BaseModel):
    """Схема для частичного обновления товара."""

    name: str | None = None
    url: str | None = None
    current_price: Decimal | None = None
    target_price: Decimal | None = None


class ProductResponse(ProductBase):
    """Схема ответа с полными данными товара из БД."""

    id: int
    current_price: Decimal | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("current_price", when_used="json")
    def _serialize_current_price(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None

    # Важно для преобразования SQLAlchemy моделей в Pydantic
    model_config = ConfigDict(from_attributes=True)
