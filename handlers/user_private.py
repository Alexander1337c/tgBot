from aiogram import types, Router, F, Bot
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import Bold, as_marked_list, as_marked_section, Italic, as_list
from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard
from database.orm_query import orm_get_cards, orm_add_card, orm_create_user
from sqlalchemy.ext.asyncio import AsyncSession

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

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
    text = as_marked_section(
        f"Добро пожаловать {message.from_user.first_name}",
        Bold('Чтобы добавить источники средств'),
        'Выберите "добавить карту"',
        'Введите ее название',
        'Отправьте',
        'По умолчанию у Вас есть Наличные с лимитом 200 byn',
        marker='✅ '

    )
    user_data = {
        'user_id': message.from_user.id,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
    }
    await orm_create_user(session, data=user_data)

    data = {
        'name': 'Наличные',
        'limit': 250,
        'user_id': message.from_user.id
    }
    await orm_add_card(session, data)
    await message.answer(text.as_html(), reply_markup=MAIN_MENU)


# @user_private_router.message((F.text.lower().contains('меню') | F.text.lower().contains('menu')))
@user_private_router.message(or_f(Command('menu'), F.text.lower() == 'меню'))
async def cmd_menu(message: types.Message):

    await message.answer(text='<strong>Вот меню</strong>',reply_markup=get_keyboard(
        'Остаток по источникам',
        'Расходы',
        'Доходы',
        'Статистика по категориям',
        'Статистика по источникам',
        'Назад в меню',
        placeholder='Введите сумму',
        sizes=(2, 2)
    ))

@user_private_router.message((F.text == 'Назад в меню') | (F.text == 'Выйти'))
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


@user_private_router.message(F.text == 'Удалить карту')
async def cmd_get_card(message: types.Message, session: AsyncSession):
    await message.answer('Hello')
    card = await orm_get_cards(session)
    text = as_marked_list(
        Bold('Ваши карты:'),
        '\n✅ '.join([item.name for item in card]),
        marker='✅ ',
    )
    await message.answer(text.as_html())
