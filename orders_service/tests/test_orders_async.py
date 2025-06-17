# orders_service/tests/test_orders_async.py
import pytest
from orders_service.domain.entities import OrderStatus

@pytest.mark.anyio
async def test_create_and_get_order(async_client):
    # 1) создаём новый заказ
    payload = {
        "user_id": "user123",
        "amount": 42.5,
        "description": "Sample order"
    }
    resp = await async_client.post("/orders", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    # Проверяем, что статус PENDING
    assert data["status"] == OrderStatus.PENDING.value
    assert data["user_id"] == "user123"
    assert float(data["amount"]) == 42.5

    order_id = data["order_id"]
    # 2) проверяем GET /orders
    resp_list = await async_client.get("/orders")
    assert resp_list.status_code == 200
    orders = resp_list.json()
    assert any(o["order_id"] == order_id for o in orders)

    # 3) проверяем GET /orders/{order_id}
    resp_get = await async_client.get(f"/orders/{order_id}")
    assert resp_get.status_code == 200
    single = resp_get.json()
    assert single["order_id"] == order_id
    assert single["description"] == "Sample order"

@pytest.mark.anyio
async def test_invalid_order_not_found(async_client):
    # Попытка получить несуществующий заказ должна вернуть 404
    resp = await async_client.get("/orders/nonexistent-id")
    assert resp.status_code == 404
    assert "not found" in resp.text.lower()
