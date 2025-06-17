from pydantic import BaseModel, Field
from typing import List


class CreateOrderRequest(BaseModel):
    user_id: str
    amount: float = Field(1.0, description="Сумма заказа (по умолчанию 1)")
    description: str


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    amount: float
    description: str
    status: str


class ListOrdersResponse(BaseModel):
    orders: List[OrderResponse]


class AccountCreateRequest(BaseModel):
    user_id: str


class AccountCreateResponse(BaseModel):
    user_id: str
    balance: float


class DepositRequest(BaseModel):
    amount: float


class DepositResponse(BaseModel):
    user_id: str
    balance: float


class BalanceResponse(BaseModel):
    user_id: str
    balance: float
