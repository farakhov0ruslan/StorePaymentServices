import json
from uuid import uuid4
from typing import Optional
from payments_service.infrastructure.db import AsyncSessionLocal
from payments_service.domain.entities import Account
from payments_service.infrastructure.models import AccountModel, InboxModel, OutboxModel
from payments_service.domain.entities import Account
from payments_service.domain.interfaces import AccountRepository, InboxRepository, OutboxRepository


class SQLAccountRepo(AccountRepository):

    async def get(self, user_id: str) -> Optional[Account]:
        async with AsyncSessionLocal() as s:
            m = await s.get(AccountModel, user_id)
            return Account(m.user_id, m.balance) if m else None

    async def save(self, account: Account):
        async with AsyncSessionLocal() as s:
            await s.merge(AccountModel(user_id=account.user_id, balance=account.balance))
            await s.commit()


class SQLInboxRepo(InboxRepository):
    async def is_processed(self, message_id: str) -> bool:
        async with AsyncSessionLocal() as s:
            return bool(await s.get(InboxModel, message_id))

    async def mark_processed(self, message_id: str):
        async with AsyncSessionLocal() as s:
            s.add(InboxModel(message_id=message_id, payload=""))
            await s.commit()


class SQLOutboxRepo(OutboxRepository):
    async def add_event(self, event_type: str, payload: dict):
        async with AsyncSessionLocal() as s:
            s.add(OutboxModel(id=str(uuid4()), event_type=event_type, payload=json.dumps(payload)))
            await s.commit()
