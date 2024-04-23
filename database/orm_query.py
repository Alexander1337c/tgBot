from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Account, User, Category
from sqlalchemy import select, update, delete

### Работа с пользователями
async def orm_create_user(session: AsyncSession, data: dict):
    obj = User(
        user_id=data['user_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
    )
    session.add(obj)
    await session.commit()




### Работа с категориями
async def orm_add_category(session: AsyncSession, data: dict):
    obj = Category(
        name=data['name'].split('-')[0],
        icon=data['name'].split('-')[1]
    )
    session.add(obj)
    await session.commit()

async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_delete_category(session, category_id):
    query = delete(Category).where(Category.id == category_id)
    await session.execute(query)
    await session.commit()


### Работа с картами
async def orm_add_card(session: AsyncSession, data: dict):
    obj = Account(
        name=data['name'],
        limit=float(data['limit']),
        user_id=data['user_id']
    )
    session.add(obj)
    await session.commit()


async def orm_get_cards(session: AsyncSession):
    query = select(Account)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_card(session: AsyncSession, card_id: int):
    query = select(Account).where(Account.id == card_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_updata_card(session: AsyncSession, card_id: int, data):
    query = update(Account).where(Account.id == card_id).values(
        name=data['name'],
        limit=float(data['limit']),
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_card(session: AsyncSession, card_id: int):
    query = delete(Account).where(Account.id == card_id)
    await session.execute(query)
    await session.commit()
