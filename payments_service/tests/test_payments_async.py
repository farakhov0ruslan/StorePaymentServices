# payments_service/tests/test_payments_async.py

import pytest
from payments_service.application.schemas import BalanceResponse, AccountCreateResponse, DepositResponse

@pytest.mark.anyio
async def test_account_lifecycle(async_client):
    # при попытке получить баланс несуществующего счёта — 404
    r0 = await async_client.get("/accounts/userX/balance")
    assert r0.status_code == 404

    # создаём счёт
    r1 = await async_client.post("/accounts", params={"user_id": "userX"})
    assert r1.status_code == 201
    data1 = r1.json()
    # структура ответа и дефолтный баланс 0.0
    assert data1 == AccountCreateResponse(user_id="userX", balance=0.0).dict()

    # сразу посмотреть баланс — он 0
    r2 = await async_client.get("/accounts/userX/balance")
    assert r2.status_code == 200
    assert r2.json() == BalanceResponse(user_id="userX", balance=0.0).dict()

    # пополнить счёт на 100.5
    r3 = await async_client.post(
        "/accounts/userX/deposit",
        json={"amount": 100.5}
    )
    assert r3.status_code == 200
    data3 = r3.json()
    assert data3 == DepositResponse(user_id="userX", balance=100.5).dict()

    # убедиться, что баланс сохранился
    r4 = await async_client.get("/accounts/userX/balance")
    assert r4.status_code == 200
    assert r4.json()["balance"] == 100.5

@pytest.mark.anyio
async def test_deposit_validation(async_client):
    # Попытка депозита с отрицательной суммой — 422
    r = await async_client.post("/accounts/foo/deposit", json={"amount": -5})
    assert r.status_code == 422
    # В теле ответа есть указание на нарушение gt=0
    body = r.json()
    assert any("gt" in e.get("msg", "") or "greater than 0" in e.get("msg", "") for e in body["detail"])
