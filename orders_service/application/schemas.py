# orders_service/application/schemas.py

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """
    Схема запроса для создания нового заказа.
    """
    user_id: str = Field(
        ..., description="Уникальный идентификатор пользователя, создающего заказ")
    amount: float = Field(
        ..., gt=0, description="Сумма заказа (должна быть положительным числом)")
    description: str = Field(
        ..., description="Описание или наименование заказа")


class OrderOut(BaseModel):
    """
    Схема ответа с информацией о заказе.
    """
    order_id: str = Field(
        ..., description="Уникальный идентификатор заказа")
    user_id: str = Field(
        ..., description="Идентификатор пользователя, которому принадлежит заказ")
    amount: float = Field(
        ..., description="Сумма заказа")
    status: str = Field(
        ..., description="Текущий статус заказа (например, PENDING, PAID, FAILED)")
    description: str = Field(
        ..., description="Описание заказа")
