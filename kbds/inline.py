from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MenuCallBack(CallbackData, prefix='categories'):
    level: int
    menu_name: str
    cost: float | None = None
    category: int | None = None
    card: int | None = None

# для callback кнопок


def get_callback_btns(
    *,
    btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()
# для url кнопок


def get_url_btns(
    *,
    btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()

# mix из url and callback кнопок


def get_mix_btns(
    *,
    btns: dict[str, str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))
    return keyboard.adjust(*sizes).as_markup()


def get_user_category_btns(*, level: int, categories: list, cost: float, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for c in categories:
        if c.name != 'Доходы':
            keyboard.add(InlineKeyboardButton(text=f'{c.icon} {c.name}', callback_data=MenuCallBack(
                level=level+1,menu_name=c.name, category_name=c.name, category=c.id, cost=cost).pack()))
    another_keyboard = InlineKeyboardBuilder()
    another_keyboard.add(InlineKeyboardButton(text='❎ Отмена', callback_data=MenuCallBack(
        level=level, menu_name='cancel').pack()))
    another_keyboard.add(InlineKeyboardButton(text='💸 Доход', callback_data=MenuCallBack(
        level=level+1, menu_name=c.name, act='income', category=9, cost=cost).pack()))
    another_keyboard.adjust(2)
    return keyboard.adjust(*sizes).attach(another_keyboard).as_markup()


def get_user_card_btns(*, level: int, cards: list, category: int, cost: float, sizes: tuple[int] = (1,)):

    keyboard = InlineKeyboardBuilder()
    for c in cards:
        keyboard.add(InlineKeyboardButton(text=f'{c.name}', callback_data=MenuCallBack(
            level=level+1, menu_name=c.name, card=c.id, category=category, cost=cost).pack()))
    another_keyboard = InlineKeyboardBuilder()
    another_keyboard.add(InlineKeyboardButton(text='❎ Отмена', callback_data=MenuCallBack(
        level=level, menu_name='cancel').pack())).adjust()
    another_keyboard.add(InlineKeyboardButton(text='< Назад', callback_data=MenuCallBack(
        level=level-1, menu_name=c.name, card=c.id, cost=cost).pack()))
    another_keyboard.adjust(2)
    return keyboard.adjust(*sizes).attach(another_keyboard).as_markup()
