from fastapi import APIRouter
from api_gateway.services import PaymentsService
from api_gateway.schemas import AccountCreateRequest, AccountCreateResponse, DepositRequest, \
    BalanceResponse

router = APIRouter()

@router.post("/accounts", response_model=AccountCreateResponse, status_code=201)
async def create_account(body: AccountCreateRequest):
    return await PaymentsService().create_account(body.user_id)


@router.post("/accounts/{user_id}/deposit", response_model=BalanceResponse)
async def deposit(user_id: str, body: DepositRequest):
    return await PaymentsService().deposit(user_id, body.amount)


@router.get("/accounts/{user_id}/balance", response_model=BalanceResponse)
async def balance(user_id: str):
    return await PaymentsService().get_balance(user_id)
