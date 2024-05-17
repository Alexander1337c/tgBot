from sqlalchemy.ext.asyncio import AsyncSession
from kbds.inline import get_user_category_btns, get_user_card_btns, get_date_stat_btns, get_year_stat_btns, get_month_stat_btns
from kbds.reply import get_keyboard
from database.orm_query import orm_get_categories, orm_get_cards, orm_get_transactions_categories_month, orm_get_transactions_category_year, orm_get_spending_account, orm_get_all_transactions_year, orm_get_all_transactions_month
from aiogram import types
from datetime import date
import calendar


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


def level_stat(level: int, month:str, year:int, text:str):
    if level == 0:
        kbds = get_date_stat_btns(level=level, current_date={'month': month, 'year': year}, text=text)
    if level == 1:
        kbds = get_month_stat_btns(level=level, current_date={'month': month, 'year': year}, text=text)
    if level == 2:
        kbds = get_year_stat_btns(level=level, current_date={'month': month, 'year': year}, text=text)
    return kbds

async def main_menu_stat(
        session: AsyncSession,
        text: str,
        level:int,
        user_id:int | None = None,
        current_month: int | None = None,
        current_year: int | None = None
        ):
    text_answer = ''
    month = date.today().strftime("%B") if not current_month else calendar.month_name[current_month]
    year = date.today().year if not current_year else current_year

    if text == 'Статистика по категориям':
        spendings = None
        if current_month and not current_year or not current_month and not current_year:
            spendings = await orm_get_transactions_categories_month(session, user_id, current_month)
        elif current_year:
            cur_month = date.today().month if not current_month else current_month
            spendings = await orm_get_transactions_category_year(session, user_id, cur_year=year, cur_month=cur_month)
        total_sum = sum([spent[3] for spent in spendings])
        text_answer = [f'{spent[2]}  {spent[1]} - <strong>{spent[3]}</strong>  (<b><i>{round((spent[3]/total_sum)*100, 2)} %</i></b>)' for spent in spendings]
        text_answer = f'Траты за    <b>{month}, {year}</b>\n----------------------------\n' + '\n'.join(text_answer) + f'\n----------------------------\nОбщая сумма:    <b>{total_sum}</b> руб'
#################################################################################################
    if text == 'Все транзакции':
        transactions = None
        if current_month and not current_year or not current_month and not current_year:
            transactions = await orm_get_all_transactions_month(session, user_id, current_month)
        elif current_year:
            cur_month = date.today().month if not current_month else current_month
            transactions = await orm_get_all_transactions_year(session, user_id, year, cur_month)
        text_answer = [
        f'{tran.amount} | {tran.account.name} | {tran.category.icon} {tran.category.name} | {str(tran.created).split(".")[0]}\n----------------------------' for tran in transactions]
        text_answer = f'{text} за    <b>{month}, {year}</b>\n----------------------------------------\n' + '\n'.join(text_answer)
###################################################################################################
    
    if text == 'Расходы' or text == 'Доходы':
        accounts = await orm_get_spending_account(session, user_id, cur_month=current_month, cur_year=year, income=text)  
        total = sum([spent[2] for spent in accounts])
        text_answer = [
        f'{spent[1]} - <strong>{spent[2]}</strong>  (<b><i>{round((spent[2]/total)*100, 2)} %</i></b>)' for spent in accounts]
        text_answer = f'{text} за    <b>{month}, {year}</b>\n----------------------------\n' + '\n'.join(text_answer) + f'\n----------------------------\nОбщая сумма:    <b>{total}</b> руб'

    return text_answer, level_stat(level, month=month, year=year, text=text)

