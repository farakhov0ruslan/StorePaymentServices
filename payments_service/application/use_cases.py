from payments_service.domain.entities import Account, PaymentResult
from payments_service.domain.interfaces import AccountRepository, OutboxRepository, InboxRepository


class CreateAccount:
    def __init__(self, repo: AccountRepository):
        self.repo = repo

    async def execute(self, user_id: str):
        account = Account(user_id)
        await self.repo.save(account)
        return account


class Deposit:
    def __init__(self, repo: AccountRepository):
        self.repo = repo

    async def execute(self, user_id: str, amount: float):
        account = await self.repo.get(user_id)
        if account is None:
            raise ValueError(f"Account '{user_id}' not found")
        account.balance += amount
        await self.repo.save(account)
        return account


class ProcessPayment:
    def __init__(self, acc_repo: AccountRepository,
                 in_repo: InboxRepository,
                 out_repo: OutboxRepository):
        self.acc_repo = acc_repo
        self.in_repo = in_repo
        self.out_repo = out_repo

    async def execute(self, message_id: str, user_id: str, order_id: str, amount: float):
        if await self.in_repo.is_processed(message_id):
            return PaymentResult.FAILED
        account = await self.acc_repo.get(user_id)
        if account is None:
            await self.out_repo.add_event(
                "payment_failed",
                {"user_id": user_id, "order_id": order_id, "amount": amount}
            )
            await self.in_repo.mark_processed(message_id)
            return PaymentResult.FAILED
        if account.balance >= amount:
            account.balance -= amount
            await self.acc_repo.save(account)
            await self.out_repo.add_event("payment_success",
                                          {"user_id": user_id,
                                           "order_id": order_id,
                                           "amount": amount})
            result = PaymentResult.SUCCESS
        else:
            await self.out_repo.add_event("payment_failed",
                                          {"user_id": user_id,
                                           "order_id": order_id,
                                           "amount": amount})
            result = PaymentResult.FAILED
        await self.in_repo.mark_processed(message_id)
        return result
