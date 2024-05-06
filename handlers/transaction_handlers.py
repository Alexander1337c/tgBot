from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import Bold, as_marked_list, as_marked_section, Italic, as_list
from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns, MenuCallBack
from .user_private import MAIN_MENU, SUB_MENU
from database.orm_query import orm_get_cards, orm_add_card, orm_create_user, orm_get_user, orm_get_categories, orm_get_card, orm_add_transaction, orm_get_category, orm_updata_card
from sqlalchemy.ext.asyncio import AsyncSession
from .inline_kb_level_menu import get_menu_content

transaction_private_router = Router()
transaction_private_router.message.filter(ChatTypeFilter(['private']))


@transaction_private_router.message(or_f(F.text.replace('.', '').isdigit(), F.text.replace(',', '').isdigit()))
async def cmd_add_transaction(message: types.Message, session: AsyncSession):
    if await orm_get_cards(session, message.from_user.id):
        menu_name, reply_markup = await get_menu_content(session, level=0, cost=float(message.text.replace(',', '.')))
        return await message.answer(menu_name, reply_markup=reply_markup)
    return await message.answer('У вас пока нет источников средств.\nДобавьте пожалуйста выбрав <strong>"Добавить карту"</strong>', reply_markup=MAIN_MENU)

async def add_transaction(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    income = True if callback_data.category == 9 else False
    await orm_add_transaction(
        session,
        user_id=user.id,
        account_id=callback_data.card,
        amount=callback_data.cost,
        category_id=callback_data.category,
        income=income)
    current_balance = await orm_get_card(session, callback_data.card)
    if income:
        res = float(current_balance.balance)+float(callback_data.cost)
    else:
        res = float(current_balance.balance)-float(callback_data.cost)
    data = {
        'name':callback_data.menu_name,
        'balance': res
    }
    category = await orm_get_category(session, int(callback_data.category))
    await orm_updata_card(session, card_id=callback_data.card, data=data)
    return await callback.message.edit_text(f'Транзакция:\n Источник: {callback_data.menu_name}\n Сумма: {callback_data.cost}\n В категорию:  {category.icon} {category.name}')


@transaction_private_router.callback_query(MenuCallBack.filter())
async def cmd_get_card(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    if callback_data.level == 2:
        await add_transaction(callback, callback_data, session)
        return
    if callback_data.menu_name == 'cancel':
        return await callback.message.edit_text(f'Транзакция отменена')
    menu_name, reply_markup = await get_menu_content(session, level=callback_data.level, cost=callback_data.cost, category=callback_data.category, user_id=callback.from_user.id)
    await callback.message.edit_text(menu_name, reply_markup=reply_markup)
