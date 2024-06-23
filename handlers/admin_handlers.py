from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from .user_private import cmd_back_menu
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.reply import get_keyboard
from kbds.inline import get_callback_btns
from database.orm_query import orm_add_category, orm_get_categories, orm_delete_category

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    'Добавить категорию',
    'Удалить категорию',
    'Выйти',
    placeholder='Выберите действие',
    sizes=(2,),
)

class AddCategory(StatesGroup):
    name = State()

@admin_router.message(Command('admin'))
async def cmd_admin(message: types.Message, session: AsyncSession):
    await message.answer('Меню админа', reply_markup=ADMIN_KB)

@admin_router.message(StateFilter(None), F.text == 'Добавить категорию')
async def cmd_add_category(message: types.Message, state: FSMContext):
    await message.answer('Введите название категории,\n<strong>Например:</strong>\nКатегория-💊', reply_markup=get_keyboard(
        'Отмена',
        sizes=(1,)
    ))
    await state.set_state(AddCategory.name)

@admin_router.message(AddCategory.name, F.text)
async def cmd_add_name_category(message: types.Message, state: FSMContext, session: AsyncSession):
    if len(message.text) < 3:
        await message.answer('Некоректный ввод. Введите минимум 3 символа')
        return
    await state.update_data(name=message.text)
    data = await state.get_data()
    await orm_add_category(session, data)
    await message.answer('Категория добавлена', reply_markup=ADMIN_KB)
    await state.clear()


@admin_router.message(F.text == 'Удалить категорию')
async def cmd_get_categories(message: types.Message, session: AsyncSession):
    for category in await orm_get_categories(session):
        await message.answer(f'{category.name}-{category.icon}', reply_markup=get_callback_btns(btns={
            'Удалить': f'del_{category.id}',
        }))

    await message.answer('Категории ⏫')


@admin_router.callback_query(F.data.startswith('del_'))
async def cmd_delete_category(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    await orm_delete_category(session, int(category_id))

    await callback.answer('Категория удалена')
    await callback.message.answer(reply_markup=ADMIN_KB)