import json
from uuid import uuid4
from sqlalchemy import select
from orders_service.domain.entities import Order, OrderStatus
from orders_service.domain.interfaces import OrderRepository, OutboxRepository
from orders_service.infrastructure.db import AsyncSessionLocal
from orders_service.infrastructure.models import OrderModel, OutboxModel


class SQLAlchemyOrderRepository(OrderRepository):

    async def add(self, order: Order) -> None:
        async with AsyncSessionLocal() as session:
            orm = OrderModel(
                id=order.id,
                user_id=order.user_id,
                amount=order.amount,
                description=order.description,
                status=order.status
            )
            session.add(orm)
            await session.commit()

    async def list(self) -> list[Order]:
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(OrderModel))
            models = res.scalars().all()
            orders: list[Order] = []
            for m in models:
                o = Order(m.user_id, m.amount, m.description)
                o.id, o.status = m.id, m.status
                orders.append(o)
            return orders

    async def get(self, order_id: str) -> Order | None:
        async with AsyncSessionLocal() as session:
            m = await session.get(OrderModel, order_id)
            if not m:
                return None
            o = Order(m.user_id, m.amount, m.description)
            o.id, o.status = m.id, m.status
            return o


class SQLAlchemyOutboxRepository(OutboxRepository):

    async def add_event(self, event_type: str, payload: dict) -> None:
        async with AsyncSessionLocal() as session:
            ev = OutboxModel(
                id=str(uuid4()),
                event_type=event_type,
                payload=json.dumps(payload)
            )
            session.add(ev)
            await session.commit()
