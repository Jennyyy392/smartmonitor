"""Тесты API-эндпоинтов для работы с товарами.

Проверяем полный CRUD-цикл через HTTP-слой приложения:
создание, получение списка, получение по ID, обновление и удаление.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient):
    """Тест создания товара через API."""
    payload = {
        "name": "Test Product",
        "url": "https://example.com/test",
        "target_price": 1000.0,
    }

    response = await client.post("/api/v1/products/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["url"] == "https://example.com/test"
    assert data["target_price"] == 1000.0
    assert "id" in data
    assert data["current_price"] is None


@pytest.mark.asyncio
async def test_get_products(client: AsyncClient):
    """Тест получения списка товаров."""
    # Сначала создаем товар
    payload = {
        "name": "Test Product",
        "url": "https://example.com/test",
        "target_price": 1000.0,
    }
    await client.post("/api/v1/products/", json=payload)

    # Получаем список
    response = await client.get("/api/v1/products/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_product_by_id(client: AsyncClient):
    """Тест получения товара по ID."""
    # Создаем товар
    payload = {
        "name": "Test Product",
        "url": "https://example.com/test",
        "target_price": 1000.0,
    }
    create_response = await client.post("/api/v1/products/", json=payload)
    product_id = create_response.json()["id"]

    # Получаем по ID
    response = await client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Product"


@pytest.mark.asyncio
async def test_get_product_not_found(client: AsyncClient):
    """Тест получения несуществующего товара (должен вернуть 404)."""
    response = await client.get("/api/v1/products/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


@pytest.mark.asyncio
async def test_update_product(client: AsyncClient):
    """Тест обновления товара."""
    # Создаем товар
    payload = {
        "name": "Test Product",
        "url": "https://example.com/test",
        "target_price": 1000.0,
    }
    create_response = await client.post("/api/v1/products/", json=payload)
    product_id = create_response.json()["id"]

    # Обновляем
    update_payload = {"name": "Updated Product", "target_price": 2000.0}
    response = await client.put(f"/api/v1/products/{product_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert data["target_price"] == 2000.0


@pytest.mark.asyncio
async def test_delete_product(client: AsyncClient):
    """Тест удаления товара."""
    # Создаем товар
    payload = {
        "name": "Test Product",
        "url": "https://example.com/test",
        "target_price": 1000.0,
    }
    create_response = await client.post("/api/v1/products/", json=payload)
    product_id = create_response.json()["id"]

    # Удаляем
    response = await client.delete(f"/api/v1/products/{product_id}")

    assert response.status_code == 204

    # Проверяем, что товар удален
    get_response = await client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404
