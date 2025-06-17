from sqlalchemy import Column, String, Float
from payments_service.infrastructure.db import Base


class AccountModel(Base):
    __tablename__ = "accounts"
    user_id = Column(String, primary_key=True)
    balance = Column(Float, nullable=False)


class InboxModel(Base):
    __tablename__ = "inbox"
    message_id = Column(String, primary_key=True)
    payload = Column(String, nullable=False)


class OutboxModel(Base):
    __tablename__ = "outbox"
    id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)
    payload = Column(String, nullable=False)
