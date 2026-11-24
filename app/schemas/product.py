"""Pydantic-схемы для товара SmartMonitor."""

from datetime import datetime
from decimal import Decimal

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)


class ProductBase(BaseModel):
    """Базовые поля товара, общие для создания и ответа."""

    name: str = Field(..., min_length=2, max_length=100, description="Название товара")
    url: str = Field(..., description="Ссылка на товар (http/https)")
    target_price: Decimal | None = Field(
        None, gt=0, max_digits=12, decimal_places=2, description="Желаемая цена для уведомления"
    )

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        return str(AnyHttpUrl(value))

    @field_serializer("target_price", when_used="json")
    def _serialize_target_price(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class ProductCreate(ProductBase):
    """Схема для создания нового товара."""

    pass


class ProductUpdate(BaseModel):
    """Схема для частичного обновления товара."""

    name: str | None = Field(None, min_length=2, max_length=100, description="Название товара")
    url: str | None = Field(None, description="Ссылка на товар (http/https)")
    current_price: Decimal | None = Field(
        None, gt=0, max_digits=12, decimal_places=2, description="Текущая цена"
    )
    target_price: Decimal | None = Field(
        None, gt=0, max_digits=12, decimal_places=2, description="Желаемая цена для уведомления"
    )

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str | None) -> str | None:
        return str(AnyHttpUrl(value)) if value is not None else None


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
