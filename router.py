from fastapi import APIRouter
from schemas import *
from database import update_balances, input_transactions, async_session, get_balance, get_transactions

router = APIRouter()

@router.post("/deposit")
async def deposit_endpoint(data: DepositRequest):
    async with async_session() as session:
        await input_transactions(
            user_id = data.user_id,
            type_of = "deposit",
            currency = data.currency,
            amount = data.amount,
            session = session
        )

        await update_balances(
            user_id = data.user_id,
            currency = data.currency,
            amount = data.amount,
            type_of = "deposit", 
            session = session
        )
        await session.commit()
        return {"id": data.user_id, "result": f"Баланс успешно пополнен на {data.amount} {data.currency}"}

@router.post("/transaction")
async def transaction_endpoint(data: TransactionRequest):
    async with async_session() as session:
        await input_transactions(
            user_id = data.user_id,
            type_of = "transaction",
            currency = data.currency,
            amount = data.amount,
            session = session
        )

        await update_balances(
            user_id = data.user_id,
            currency = data.currency,
            amount = data.amount,
            type_of = "transaction",
            session = session
        )

        await session.commit()
        return {"id": data.user_id, "result": f"Покупка {data.amount} {data.currency} успешно совершена"}

@router.post("/transfer")
async def transfer_endpoint(data: TransferRequest):
    async with async_session() as session:
        result = await input_transactions(
            user_id = data.user_id,
            type_of = "transfer",
            currency = data.currency,
            amount = data.amount,
            session = session,
            user_id_2 = data.user_id_2
        )

        if result is False:
            return {"id": data.user_id, "result": "Невозможно сделать перевод - пользователя кому переводят не существует"}

        await update_balances(
            user_id = data.user_id,
            currency = data.currency,
            amount = data.amount,
            type_of = "transfer",
            session = session
        )
        await session.commit()
        return {"id": data.user_id, "result": f"Перевод {data.user_id_2} пользователю в размере {data.amount} {data.currency} успешно совершен"}

@router.get("/balance")
async def balance_endpoint(user_id: int):
    async with async_session() as session:
        rows = await get_balance(
            user_id = user_id, 
            session = session)

        if not rows:
            return {"id": user_id, "result": "Баланс у юзера не найден"}
        
        return {"id": user_id, "result": f"Баланс - {rows}"}

@router.get("/transaction_list")
async def transaction_list_endpoint(user_id: int, type_of: str = None, lower_amount: int = 0, higher_amount: int = 999999, lower_date: datetime = datetime(2020, 1, 1), higher_date: datetime = datetime.now()):
    async with async_session() as session:
        rows = await get_transactions(
            user_id=user_id,
            type_of=type_of,
            lower_amount=lower_amount,
            higher_amount=higher_amount,
            lower_date=lower_date,
            higher_date=higher_date,
            session=session
        )

        if not rows:
            return {"id": user_id, "result": "Опреации не найдены"}
        
        result_list = [
            {"type": r.type_of, "currency": r.currency, "amount": r.amount}
            for r in rows
        ]
        
        return {"id": user_id, "result": f"Список транзакций - {result_list}"}