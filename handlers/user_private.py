from datetime import datetime, date
from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import Bold, as_marked_list, as_marked_section, Italic, as_list
from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns, StatCallBack
from handlers.inline_kb_level_menu import main_menu_stat


from database.orm_query import orm_get_cards, orm_add_card, orm_create_user, orm_get_user 
from sqlalchemy.ext.asyncio import AsyncSession


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

SUB_MENU = get_keyboard(
    'Остаток по источникам',
    'Расходы',
    'Доходы',
    'Статистика по категориям',
    'Все транзакции',
    'На главную',
    placeholder='Введите сумму',
    sizes=(2, 2)
)

MAIN_MENU = get_keyboard(
    "Меню",
    "О боте",
    "Добавить карту",
    "Источники средств",
    placeholder='Введите сумму',
    sizes=(2, 2)
)


@user_private_router.message(CommandStart())
async def starc_cmd(message: types.Message, bot: Bot, session: AsyncSession):
    if await orm_get_user(session, int(message.from_user.id)):
        return await message.answer(f'Добро пожаловать, <strong>{message.from_user.first_name}!</strong>', reply_markup=MAIN_MENU)
    else:
        text = as_marked_section(
            f"Добро пожаловать {message.from_user.first_name}",
            Bold('Чтобы добавить источники средств'),
            'Выберите "добавить карту"',
            'Введите ее название',
            'Отправьте',
            'Введите сумму для внесения платежа',
            marker='✅ '
        )
        user_data = {
            'user_id': message.from_user.id,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
        }
        await orm_create_user(session, data=user_data)
        await message.answer(text.as_html(), reply_markup=MAIN_MENU)


# @user_private_router.message((F.text.lower().contains('меню') | F.text.lower().contains('menu')))
@user_private_router.message(or_f(Command('menu'), F.text.lower() == 'меню'))
async def cmd_menu(message: types.Message):

    await message.answer(text='<strong>Вот меню</strong>', reply_markup=SUB_MENU)


@user_private_router.message((F.text == 'На главную') | (F.text == 'Выйти'))
async def cmd_back_menu(message: types.Message):
    await message.answer(text='Главная', reply_markup=MAIN_MENU)


@user_private_router.message(or_f(Command('about'), (F.text.lower() == 'о боте')))
async def cmd_about(message: types.Message):
    text = as_marked_section(
        Bold('Помогает: '),
        'Учитывать расходы/доходы',
        'Получать статистику по категориям/картам',
        marker="✅ "
    )
    await message.answer(text.as_html())

command_list = {'Статистика по категориям','Все транзакции', 'Расходы', 'Доходы'}
@user_private_router.message(F.text.in_(command_list))
async def cmd_balance_total(message: types.Message, session: AsyncSession):
    
    text, reply_markup = await main_menu_stat(session, text=message.text, level=0, user_id=message.from_user.id)
    await message.answer(text=text, reply_markup=reply_markup)

@user_private_router.callback_query(StatCallBack.filter())
async def date_menu(callback: types.CallbackQuery, callback_data: StatCallBack, session: AsyncSession):

    print(callback_data)
    text, reply_markup = await main_menu_stat(session, level=callback_data.level, text=callback_data.text, user_id=callback.from_user.id, current_month=callback_data.cur_month, current_year=callback_data.cur_year)
    
    await callback.message.edit_text(text=text, reply_markup=reply_markup)
    
    await callback.answer()

@user_private_router.message(F.text == 'Остаток по источникам')
async def cmd_stat_for_category(message: types.Message, session: AsyncSession):
    cards = await orm_get_cards(session, int(message.from_user.id))
    if cards:
        text = [f'{card.name} <strong>остаток</strong> {card.balance}' for card in cards]
        return await message.answer('\n'.join(text))
    return await message.answer(f'У вас пока нет источников средств', reply_markup=MAIN_MENU)

    
# ///##############################################################3 для тестированя

