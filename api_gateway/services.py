import httpx
from fastapi import HTTPException

from api_gateway.config import settings
from api_gateway.utils import unwrap_httpx_error


class OrdersService:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.ORDER_SERVICE_URL)

    async def create_order(self, user_id: str, amount: float, description: str):
        try:
            resp = await self.client.post(
                "/orders", json={"user_id": user_id, "amount": amount, "description": description},
                headers={"Content-Type": "application/json", "X-Some-Header": "value"}
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise unwrap_httpx_error(e)
        return resp.json()

    async def list_orders(self):
        try:
            resp = await self.client.get("/orders")
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise unwrap_httpx_error(e)
        return resp.json()

    async def get_order(self, order_id: str):
        try:
            resp = await self.client.get(f"/orders/{order_id}")
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code,
                                detail=e.response.json())
        return resp.json()


class PaymentsService:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=settings.PAYMENT_SERVICE_URL)

    async def create_account(self, user_id: str):
        try:
            resp = await self.client.post("/accounts", params={"user_id": user_id})
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise unwrap_httpx_error(e)
        return resp.json()

    async def deposit(self, user_id: str, amount: float):
        try:
            resp = await self.client.post(f"/accounts/{user_id}/deposit", json={"amount": amount})
            resp.raise_for_status()

        except httpx.HTTPStatusError as e:
            raise unwrap_httpx_error(e)
        return resp.json()

    async def get_balance(self, user_id: str):
        try:
            resp = await self.client.get(f"/accounts/{user_id}/balance")
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise unwrap_httpx_error(e)
        return resp.json()
