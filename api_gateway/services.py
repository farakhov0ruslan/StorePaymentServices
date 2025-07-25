import httpx
from fastapi import HTTPException

from api_gateway.config import settings
from api_gateway.utils import unwrap_httpx_error
import os
from grpc import aio
from google.protobuf import empty_pb2
from api_gateway.grpc import order_service_pb2, order_service_pb2_grpc


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


ORDER_SERVICE_GRPC_ADDR = os.getenv("ORDER_SERVICE_GRPC", "order_service:50051")


class OrdersGrpcClient:
    def __init__(self):
        # создаём канал и stub
        self._channel = aio.insecure_channel(ORDER_SERVICE_GRPC_ADDR)
        self._stub = order_service_pb2_grpc.OrderServiceStub(self._channel)

    async def create_order(self, user_id: str, amount: float, description: str) -> dict:
        req = order_service_pb2.CreateOrderRequest(
            user_id=user_id,
            amount=amount,
            description=description,
        )
        resp = await self._stub.CreateOrder(req)
        return {
            "order_id": resp.order_id,
            "user_id": resp.user_id,
            "amount": resp.amount,
            "description": resp.description,
            "status": resp.status,
        }

    async def get_order(self, order_id: str) -> dict:
        req = order_service_pb2.GetOrderRequest(order_id=order_id)
        resp = await self._stub.GetOrder(req)
        return {
            "order_id": resp.order_id,
            "user_id": resp.user_id,
            "amount": resp.amount,
            "description": resp.description,
            "status": resp.status,
        }

    async def list_orders(self) -> list[dict]:
        resp = await self._stub.ListOrders(empty_pb2.Empty())
        return [
            {
                "order_id": o.order_id,
                "user_id": o.user_id,
                "amount": o.amount,
                "description": o.description,
                "status": o.status,
            }
            for o in resp.orders
        ]
