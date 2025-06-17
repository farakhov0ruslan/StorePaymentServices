from pydantic import BaseModel, Field
from enum import Enum


class AccountCreateResponse(BaseModel):
    """
    Ответ после создания счёта.
    """
    user_id: str = Field(..., description="Уникальный идентификатор пользователя")
    balance: float = Field(..., description="Текущий баланс счёта")


class DepositRequest(BaseModel):
    """
    Тело запроса при пополнении счёта.
    """
    amount: float = Field(..., gt=0, description="Сумма пополнения (положительное число)")


class DepositResponse(BaseModel):
    """
    Ответ после успешного пополнения счёта.
    """
    user_id: str = Field(..., description="Идентификатор пользователя")
    balance: float = Field(..., description="Новый баланс счёта")


class BalanceResponse(BaseModel):
    """
    Ответ на запрос текущего баланса счёта.
    """
    user_id: str = Field(..., description="Идентификатор пользователя")
    balance: float = Field(..., description="Текущий баланс счёта")


class PaymentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class PaymentEvent(BaseModel):
    """
    Схема события оплаты для Outbox (и/или Inbox).
    """
    message_id: str = Field(..., description="Уникальный идентификатор сообщения из очереди")
    user_id: str = Field(...,
                         description="Идентификатор пользователя, по которому списываются/зачисляются средства")
    amount: float = Field(..., description="Сумма операции")
    status: PaymentStatus = Field(..., description="Результат обработки платежа")
