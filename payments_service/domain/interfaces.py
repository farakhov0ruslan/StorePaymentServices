from abc import ABC, abstractmethod
from payments_service.domain.entities import Account


class AccountRepository(ABC):
    @abstractmethod
    async def get(self, user_id: str) -> Account | None: ...

    @abstractmethod
    async def save(self, account: Account) -> None: ...


class OutboxRepository(ABC):
    @abstractmethod
    async def add_event(self, event_type: str, payload: dict) -> None: ...


class InboxRepository(ABC):
    @abstractmethod
    async def is_processed(self, message_id: str) -> bool: ...

    @abstractmethod
    async def mark_processed(self, message_id: str) -> None: ...
