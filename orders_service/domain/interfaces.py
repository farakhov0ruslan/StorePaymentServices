from abc import ABC, abstractmethod
from typing import List, Optional
from orders_service.domain.entities import Order


class OrderRepository(ABC):
    @abstractmethod
    async def add(self, order: Order) -> None: ...

    @abstractmethod
    async def list(self) -> List[Order]: ...

    @abstractmethod
    async def get(self, order_id: str) -> Optional[Order]: ...


class OutboxRepository(ABC):
    @abstractmethod
    async def add_event(self, event_type: str, payload: dict) -> None: ...
