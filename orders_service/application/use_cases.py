from typing import List
from orders_service.domain.entities import Order
from orders_service.domain.interfaces import OrderRepository, OutboxRepository
from orders_service.application.schemas import OrderCreate, OrderOut


class CreateOrderUseCase:
    def __init__(self, repo: OrderRepository, outbox: OutboxRepository):
        self.repo = repo
        self.outbox = outbox

    async def execute(self, dto: OrderCreate) -> OrderOut:
        order = Order(dto.user_id, dto.amount, dto.description)
        # 1) сохраняем заказ
        await self.repo.add(order)
        # 2) пишем событие в outbox
        await self.outbox.add_event(
            event_type="order_created",
            payload={
                "order_id": order.id,
                "user_id": order.user_id,
                "amount": order.amount,
                "description": order.description
            }
        )
        return OrderOut(
            order_id=order.id,
            user_id=order.user_id,
            amount=order.amount,
            description=order.description,
            status=order.status.value,

        )


class ListOrdersUseCase:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def execute(self) -> List[OrderOut]:
        orders = await self.repo.list()
        return [
            OrderOut(
                order_id=o.id,
                user_id=o.user_id,
                amount=o.amount,
                description=o.description,
                status=o.status.value
            )
            for o in orders
        ]


class GetOrderUseCase:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def execute(self, order_id: str) -> OrderOut | None:
        o = await self.repo.get(order_id)
        if not o:
            return None
        return OrderOut(
            order_id=o.id,
            user_id=o.user_id,
            description=o.description,
            amount=o.amount,
            status=o.status.value
        )
