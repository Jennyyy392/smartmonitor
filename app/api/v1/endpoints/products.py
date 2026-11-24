"""CRUD-эндпоинты для работы с товарами (Product).

Вся бизнес-логика вынесена в сервисный слой app.services.product_service,
здесь остаётся только обработка HTTP-запросов и ответов.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services import product_service

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
):
    return await product_service.create_product(db, product_in)


@router.get("/", response_model=list[ProductResponse])
async def get_products_endpoint(db: AsyncSession = Depends(get_db)):
    return await product_service.get_all_products(db)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(product_id: int, db: AsyncSession = Depends(get_db)):
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
@router.put("/{product_id}", response_model=ProductResponse, include_in_schema=False)
async def update_product_endpoint(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    product = await product_service.update_product(db, product_id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(product_id: int, db: AsyncSession = Depends(get_db)):
    success = await product_service.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None


@router.post("/{product_id}/check-price", response_model=ProductResponse)
async def check_price_endpoint(product_id: int, db: AsyncSession = Depends(get_db)):
    """Эндпоинт для ручного запуска проверки цены (наш первый парсер!)."""
    product = await product_service.check_and_update_price(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
