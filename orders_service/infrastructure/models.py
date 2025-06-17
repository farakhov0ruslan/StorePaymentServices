from sqlalchemy import Column, String, Float, Enum
from sqlalchemy.orm import declarative_base
from orders_service.domain.entities import OrderStatus

Base = declarative_base()


class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)


class OutboxModel(Base):
    __tablename__ = "outbox"
    id = Column(String, primary_key=True)
    event_type = Column(String, nullable=False)
    payload = Column(String, nullable=False)
