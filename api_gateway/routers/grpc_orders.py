from fastapi import APIRouter, HTTPException
import grpc
from typing import List

from api_gateway.services import OrdersGrpcClient
from api_gateway.schemas import CreateOrderRequest, OrderResponse

router = APIRouter()
_client = OrdersGrpcClient()


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(dto: CreateOrderRequest):
    try:
        return await _client.create_order(dto.user_id, dto.amount, dto.description)
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or "Internal gRPC error")


@router.get("/", response_model=List[OrderResponse])
async def list_orders():
    try:
        return await _client.list_orders()
    except grpc.aio.AioRpcError as e:
        raise HTTPException(status_code=500, detail=e.details() or "Internal gRPC error")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    try:
        return await _client.get_order(order_id)
    except grpc.aio.AioRpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            # Заказ не найден — возвращаем 404
            raise HTTPException(status_code=404, detail="Order not found")
        # Любая другая ошибка — 500
        raise HTTPException(status_code=500, detail=e.details() or "Internal gRPC error")
