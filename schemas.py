from pydantic import BaseModel
from datetime import datetime

class DepositRequest(BaseModel):
    user_id: int
    amount: float
    currency: str = "RUB"

class TransactionRequest(BaseModel):
    user_id: int
    amount: float
    currency: str = "RUB"

class TransferRequest(BaseModel):
    user_id: int
    user_id_2: int
    amount: float
    currency: str = "RUB"

class BalanceRequest(BaseModel):
    user_id: int
    currency: str = "RUB"

class TransactionList(BaseModel):
    user_id: int
    lower_amount: int = 0
    higher_amount: int = 18 * 10
    lower_date: datetime = "01.01.2023"
    higher_date: datetime = datetime.now()

