import os
from sqlalchemy import Column, Integer, String, Float, DateTime, select
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

class Base(DeclarativeBase):
    pass

class balances(Base):
    __tablename__ = "balances"

    user_id = Column(Integer, nullable=False, primary_key=True)
    currency = Column(String, nullable=False, default="RUB", primary_key=True)
    amount = Column(Integer, nullable=False, default=0)

class transactions(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    type_of = Column(String, nullable=False)
    currency = Column(String, nullable=False, default="RUB")
    amount = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=True)
    user_id_2 = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://admin:password@localhost:5432/avito"
)

engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(engine, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def input_transactions(user_id, type_of, currency, amount, session, description=None, user_id_2=None) -> AsyncSession:
    if user_id_2 is not None:
        result = await session.execute(
            select(balances.user_id).where(balances.user_id == user_id_2)
        )
        true_or_false = result.scalar_one_or_none()

        if true_or_false is None:
            return False
        
        entry = transactions(
            user_id = user_id,
            type_of = type_of,
            currency = currency,
            amount = amount,
            description = description,
            user_id_2 = user_id_2
        )
    
        session.add(entry)
        return True

async def update_balances(user_id, currency, amount, type_of, session) -> AsyncSession:
        result = await session.execute(
            select(balances).where(
                balances.user_id == user_id,
                balances.currency == currency
            )
        )

        balance = result.scalar_one_or_none()

        if balance is None:
            session.add(
                balances(
                    user_id = user_id,
                    currency = currency,
                    amount = amount
                )
            )
        else:
            if type_of == "deposit":
                balance.amount += amount
            else:
                if balance.amount < amount:
                    raise ValueError("Недостаточно средств")
                balance.amount -= amount


async def get_balance(user_id, session) -> AsyncSession:
    result = await session.execute(
        select(balances.amount, balances.currency).where(
            balances.user_id == user_id
        )
    )

    rows = result.all()
    return rows
    

async def get_transactions(user_id, type_of, lower_amount, higher_amount, lower_date, higher_date, session) -> AsyncSession:
    result = select(transactions.type_of, transactions.currency, transactions.amount).where(
            transactions.user_id == user_id,
            transactions.amount.between(lower_amount, higher_amount),
            transactions.created_at.between(lower_date, higher_date)
        )

    if type_of:
        result = result.where(transactions.type_of == type_of)

    rows = await session.execute(result)
    return rows.all()

