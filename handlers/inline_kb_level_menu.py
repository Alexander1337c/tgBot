from sqlalchemy.ext.asyncio import AsyncSession
from kbds.inline import get_user_category_btns, get_user_card_btns
from database.orm_query import orm_get_categories, orm_get_cards


async def main_menu(session: AsyncSession, level, menu_name, cost):
    categoris = await orm_get_categories(session)
    kbds = get_user_category_btns(level=level, categories=categoris, cost=cost)
    return menu_name, kbds


async def choice_card(session: AsyncSession, level, menu_name, category_id, cost, user_id):
    cards = await orm_get_cards(session, user_id)
    kbds = get_user_card_btns(level=level, cards=cards, category=category_id, cost=cost)
    return menu_name, kbds


async def get_menu_content(
    sessioon: AsyncSession,
    level: int,
    user_id: int | None = None,
    cost: float | None = None,
    category: int | None = None,

):
    if level == 0:
        menu_name = 'Выберите категорию'
        return await main_menu(sessioon, level, menu_name, cost)
    if level == 1:
        menu_name = "Выберите источник"
        return await choice_card(sessioon, level, menu_name, category, cost, user_id)
    if level == 2:
        return True
