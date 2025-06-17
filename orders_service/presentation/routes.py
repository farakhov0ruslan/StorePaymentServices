from fastapi import APIRouter, Depends, HTTPException
from orders_service.application.schemas import OrderCreate, OrderOut
from orders_service.application.use_cases import (
    CreateOrderUseCase,
    ListOrdersUseCase,
    GetOrderUseCase
)
from orders_service.infrastructure.repository import (
    SQLAlchemyOrderRepository,
    SQLAlchemyOutboxRepository
)

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_repo():
    return SQLAlchemyOrderRepository()


def get_outbox_repo():
    return SQLAlchemyOutboxRepository()


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(
    dto: OrderCreate,
    order_repo=Depends(get_order_repo),
    outbox_repo=Depends(get_outbox_repo)
):
    use_case = CreateOrderUseCase(order_repo, outbox_repo)
    return await use_case.execute(dto)


@router.get("", response_model=list[OrderOut])
async def list_orders(order_repo=Depends(get_order_repo)):
    use_case = ListOrdersUseCase(order_repo)
    return await use_case.execute()


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: str, order_repo=Depends(get_order_repo)):
    use_case = GetOrderUseCase(order_repo)
    result = await use_case.execute(order_id)
    if not result:
        raise HTTPException(404, "Order not found")
    return result
