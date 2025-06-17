from enum import Enum


class Account:
    def __init__(self, user_id: str, balance: float = 0.0):
        self.user_id = user_id
        self.balance = balance


class PaymentResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
