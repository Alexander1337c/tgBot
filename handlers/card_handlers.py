from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f, StateFilter
from aiogram.utils.formatting import Bold, as_marked_list, as_marked_section
from filters.chat_types import ChatTypeFilter
from kbds.reply import get_keyboard, del_kb
from kbds.inline import get_callback_btns
from handlers.user_private import MAIN_MENU
from handlers.admin_handlers import ADMIN_KB
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_card, orm_get_cards, orm_delete_card, orm_updata_card, orm_get_card

add_card_private_router = Router()
add_card_private_router.message.filter(ChatTypeFilter(['private']))


class AddCard(StatesGroup):
    name = State()
    limit = State()

    card_for_change = None
    texts = {
        'AddCard:name': 'Введите название заново:',
        'AddCard:limit': 'Введите лимит заново:',
    }


@add_card_private_router.message(F.text == 'Источники средств')
async def get_accounts_handler(message: types.Message, session: AsyncSession):
    for card in await orm_get_cards(session):
        await message.answer(f'{card.name} лимит: {round(card.limit, 2)}', reply_markup=get_callback_btns(btns={
            'Удалить': f'delete_{card.id}',
            'Изменить': f'update_{card.id}',
        }))
    await message.answer('Список ваших источников средств')


@add_card_private_router.callback_query(F.data.startswith('delete_'))
async def delete_card_handler(callback: types.CallbackQuery, session: AsyncSession):
    card_id = callback.data.split('_')[-1]
    await orm_delete_card(session, int(card_id))

    await callback.answer('Карта удалена')
    await callback.message.answer(reply_markup=MAIN_MENU)


@add_card_private_router.callback_query(StateFilter(None), F.data.startswith('update_'))
async def update_card_handlers(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    card_id = callback.data.split('_')[-1]
    card_for_change = await orm_get_card(session, int(card_id))

    AddCard.card_for_change = card_for_change

    await callback.answer()
    await callback.message.answer('Введите название карты', reply_markup=del_kb)

    await state.set_state(AddCard.name)


# FSM код работы с состоянием


@add_card_private_router.message(StateFilter('*'), Command('отмена'))
@add_card_private_router.message(StateFilter('*'), or_f(F.text.casefold() == 'отмена', F.text == 'Отмена'))
async def cancel_add_card_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddCard.card_for_change:
        AddCard.card_for_change = None
    await state.clear()
    if message.text == 'Отмена':
        return await message.answer('Меню админа', reply_markup=ADMIN_KB)
    await message.answer('Действия отменены', reply_markup=MAIN_MENU)


@add_card_private_router.message(StateFilter('*'), Command('назад'))
@add_card_private_router.message(StateFilter('*'), F.text.casefold() == 'назад')
async def cancel_add_card_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()

    if current_state == AddCard.name:
        await message.answer('Предидущего шага нет, или введите название товара или напишите "отмена"')
        return

    previous = None
    for step in AddCard.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Вернулись к прошлому шагу\n {AddCard.texts[previous.state]}")
            return
        previous = step


@add_card_private_router.message(StateFilter(None), F.text == 'Добавить карту')
async def cmd_add_card(message: types.Message, state: FSMContext):
    await message.answer(f'Введите название карты \nНапример: КАРТА1',
                         reply_markup=get_keyboard(
                             "отмена",
                             sizes=(1,)
                         ))
    await state.set_state(AddCard.name)


@add_card_private_router.message(AddCard.name, or_f(F.text.isupper(), F.text == '.'))
async def cmd_add_name_card(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(name=AddCard.card_for_change.name)
    else:
        await state.update_data(name=message.text)
    await message.answer("Введите лимит расхода в неделюю. Например '200'")
    await state.set_state(AddCard.limit)


@add_card_private_router.message(AddCard.name)
async def cmd_add_name_card2(message: types.Message, state: FSMContext):
    await message.answer("Некоректный ввод. Только большие буквы. 'КАРТА1'")


@add_card_private_router.message(AddCard.limit, or_f(F.text.isdigit(), F.text == '.'))
async def add_card_limit_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == '.':
        await state.update_data(limit=AddCard.card_for_change.limit)
    else:
        await state.update_data(limit=message.text)
    data = await state.get_data()
    data['user_id'] = message.from_user.id
    try:
        if AddCard.card_for_change:
            await orm_updata_card(session, AddCard.card_for_change.id, data)
        else:
            await orm_add_card(session, data)
        await message.answer('Карта добавлена/изменена', reply_markup=MAIN_MENU)
        await state.clear()
    except Exception as e:
        await message.answer(f'Ошибка: \n{str(e)}', reply_markup=MAIN_MENU)
        await state.clear()
    AddCard.card_for_change = None

@add_card_private_router.message(AddCard.limit)
async def add_card_limit_handler(message: types.Message, state: FSMContext):
    await message.answer('Некоректный воод. Введите число')
