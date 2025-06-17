from fastapi import APIRouter, HTTPException
from payments_service.application.schemas import (
    AccountCreateResponse, DepositRequest,
    DepositResponse, BalanceResponse
)
from payments_service.application.use_cases import CreateAccount, Deposit
from payments_service.infrastructure.repository import SQLAccountRepo
from payments_service.logger import get_logger

logger = get_logger(__name__, "main.log")
router = APIRouter()



@router.post(
    "/accounts",
    response_model=AccountCreateResponse,
    status_code=201
)
async def create_account(user_id: str):
    acc = await CreateAccount(SQLAccountRepo()).execute(user_id)
    return AccountCreateResponse(user_id=acc.user_id, balance=acc.balance)


@router.post(
    "/accounts/{user_id}/deposit",
    response_model=DepositResponse
)
async def deposit(user_id: str, body: DepositRequest):
    try:
        acc = await Deposit(SQLAccountRepo()).execute(user_id, body.amount)
        return DepositResponse(user_id=acc.user_id, balance=acc.balance)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # любой другой «провал» → 500 Internal Server Error
        logger.exception("Неожиданная ошибка при депозите для %s", user_id)
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера, попробуйте позднее"
        )


@router.get(
    "/accounts/{user_id}/balance",
    response_model=BalanceResponse
)
async def get_balance(user_id: str):
    acc = await SQLAccountRepo().get(user_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return BalanceResponse(user_id=acc.user_id, balance=acc.balance)
