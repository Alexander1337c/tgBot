from datetime import datetime, date
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Account, User, Category, Transaction
from sqlalchemy import select, update, delete, func, extract, desc, sql
from sqlalchemy.orm import joinedload


# Работа с пользователями


async def orm_create_user(session: AsyncSession, data: dict):
    obj = User(
        user_id=data['user_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    session.add(obj)
    await session.commit()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


# Работа с категориями
async def orm_add_category(session: AsyncSession, data: dict):
    obj = Category(
        name=data['name'].split('-')[0],
        icon=data['name'].split('-')[1]
    )
    session.add(obj)
    await session.commit()

async def orm_get_category(session: AsyncSession, category_id: int):
    query = select(Category).where(Category.id==category_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_category(session, category_id):
    query = delete(Category).where(Category.id == category_id)
    await session.execute(query)
    await session.commit()


# Работа с картами
async def orm_add_card(session: AsyncSession, data: dict):
    obj = Account(
        name=data['name'],
        balance=float(data['balance']),
        user_id=data['user_id']
    )
    session.add(obj)
    await session.commit()


async def orm_get_cards(session: AsyncSession, user_id: int):
    query = select(Account).filter(Account.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_card(session: AsyncSession, card_id: int):
    query = select(Account).where(Account.id == card_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_updata_card(session: AsyncSession, card_id: int, data):
    query = update(Account).where(Account.id == card_id).values(
        name=data['name'],
        balance=float(data['balance']),
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_card(session: AsyncSession, card_id: int):
    query = delete(Account).where(Account.id == card_id)
    await session.execute(query)
    await session.commit()

# Работа с транзакциями


async def orm_add_transaction(session: AsyncSession, user_id, account_id, amount, category_id, income):
    obj = Transaction(
        user_id=user_id,
        account_id=account_id,
        amount=amount,
        category_id=category_id,
        income=income
    )
    session.add(obj)
    await session.commit()


async def orm_get_transactions_categories_month(session: AsyncSession, user_id, current_month: int | None = None):
    if not current_month:
        current_month = datetime.now().month
    query = select(Transaction.category_id, Category.name, Category.icon, func.sum(Transaction.amount).label('sum')).filter(Transaction.user_id == user_id, Transaction.income == False, extract('month', Transaction.created) == current_month).join(Transaction, Transaction.category_id == Category.id).group_by(Transaction.category_id, Category.name, Category.icon)
    result = await session.execute(query)
    return result.all()

async def orm_get_transactions_category_year(session: AsyncSession, user_id, cur_year: int, cur_month: int):
    query = select(Transaction.category_id, Category.name, Category.icon, func.sum(Transaction.amount).label('sum_2')).filter(Transaction.user_id == user_id, Transaction.income == False, extract('year', Transaction.created) == cur_year, extract('month', Transaction.created) == cur_month).join(Transaction, Transaction.category_id == Category.id).group_by(Transaction.category_id, Category.name, Category.icon)
    result = await session.execute(query)
    return result.all()



async def orm_get_all_transactions_year(session: AsyncSession, user_id, cur_year: int, cur_month: int):
    query = select(Transaction).options(joinedload(Transaction.category), joinedload(Transaction.account)).filter(Transaction.user_id == user_id, extract('year', Transaction.created)==cur_year, extract('month', Transaction.created)==cur_month).order_by(desc(Transaction.created))
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_all_transactions_month(session: AsyncSession, user_id, cur_month: int | None = None):
    if not cur_month:
        cur_month =  datetime.now().month
    query = select(Transaction).options(joinedload(Transaction.category), joinedload(Transaction.account)).filter(Transaction.user_id == user_id, extract('month', Transaction.created) == cur_month).order_by(desc(Transaction.created))
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_spending_account(session: AsyncSession, user_id, income: str, cur_month:int | None = None, cur_year:int | None = None):
    query = None
    bool_income = False
    if income == 'Доходы':
        bool_income = True
    if not cur_month:
        cur_month = datetime.now().month
        query = select(Transaction.account_id, Account.name, func.sum(Transaction.amount).label('sum')).filter(Transaction.user_id == user_id, Transaction.income == bool_income, extract("month", Transaction.created) == cur_month ).join(Transaction, Transaction.account_id == Account.id).group_by(Transaction.account_id, Account.name)
    elif cur_year and cur_month:
        query = select(Transaction.account_id, Account.name, func.sum(Transaction.amount).label('sum')).filter(Transaction.user_id == user_id, Transaction.income == bool_income, extract('year', Transaction.created) == cur_year, extract('month', Transaction.created) == cur_month ).join(Transaction, Transaction.account_id == Account.id).group_by(Transaction.account_id, Account.name)
    
    result = await session.execute(query)
    return result.all()

async def orm_get_spending_account_year(session: AsyncSession, user_id, income: str, cur_month:int, cur_year: int):
    if not cur_month:
        cur_month = datetime.now().month
    bool_income = False
    if income == 'Доходы':
        bool_income = True
    query = select(Transaction.account_id, Account.name, func.sum(Transaction.amount).label('sum')).filter(Transaction.user_id == user_id, Transaction.income == bool_income, extract('year', Transaction.created) == cur_year, extract('month', Transaction.created) == cur_month).join(Transaction, Transaction.account_id == Account.id).group_by(Transaction.account_id, Account.name)
    result = await session.execute(query)
    return result.all()