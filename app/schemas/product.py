"""Pydantic-схемы для товара SmartMonitor."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    """Базовые поля товара, общие для создания и ответа."""

    name: str = Field(..., min_length=2, max_length=100, description="Название товара")
    url: str = Field(..., description="Ссылка на товар")
    target_price: float | None = Field(
        None, description="Желаемая цена для уведомления"
    )


class ProductCreate(ProductBase):
    """Схема для создания нового товара."""

    pass


class ProductUpdate(BaseModel):
    """Схема для частичного обновления товара."""

    name: str | None = None
    url: str | None = None
    current_price: float | None = None
    target_price: float | None = None


class ProductResponse(ProductBase):
    """Схема ответа с полными данными товара из БД."""

    id: int
    current_price: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Важно для преобразования SQLAlchemy моделей в Pydantic
