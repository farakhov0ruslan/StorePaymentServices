from fastapi import APIRouter
from api_gateway.services import OrdersService
from api_gateway.schemas import CreateOrderRequest, OrderResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(dto: CreateOrderRequest):
    return await OrdersService().create_order(dto.user_id, dto.amount, dto.description)


@router.get("/", response_model=List[OrderResponse])
async def list_orders():
    return await OrdersService().list_orders()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    order = await OrdersService().get_order(order_id)
    return order
