import enum
from uuid import uuid4


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"


class Order:
    def __init__(self, user_id: str, amount: float, description: str):
        self.id = str(uuid4())
        self.user_id = user_id
        self.description = description
        self.amount = amount
        self.status = OrderStatus.PENDING
