import calendar
from datetime import date
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

###########################################################################
month = {'Янв': 1,'Фев': 2,'Мар': 3,'Апр': 4,'Май': 5,'Июн': 6,'Июл': 7,'Авг': 8,'Сен': 9,'Окт': 10,'Ноя': 11,'Дек': 12,}
class StatCallBack(CallbackData, prefix='stat'):
    level: int
    text: str
    cur_month: int | None = None
    cur_year: int | None = None



def get_date_stat_btns(*, level: int, current_date: dict, text: str, sizes: tuple[int]=(3,)):
    cur_month = month[current_date['month'][:3]]
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=f'{current_date["month"]}', callback_data=StatCallBack(level=level+1, text=text, cur_month=cur_month,cur_year=current_date['year']).pack()))
    keyboard.add(InlineKeyboardButton(text=f'{current_date["year"]}', callback_data=StatCallBack(level=level+2, text=text, cur_month=cur_month,cur_year=current_date['year']).pack()))
    return keyboard.adjust(*sizes).as_markup()



def get_month_stat_btns(*, level: int, current_date: dict, text:str, sizes: tuple[int]=(3,)):
    keyboard = InlineKeyboardBuilder()
    for n, i in month.items():
        keyboard.add(InlineKeyboardButton(text=f'{n} ✅' if n == current_date["month"][:3] else f'{n}', callback_data=StatCallBack(
            level=0, text=text, cur_month=i, cur_year=current_date['year']).pack()))
    return keyboard.adjust(*sizes).as_markup()

def get_year_stat_btns(*, level: int, current_date: dict, text:str, sizes: tuple[int]=(3,)):
        
    cur_month = month[current_date['month'][:3]]
    year_cur = date.today().year if not current_date['year'] else current_date['year']
    year_list = [i for i in range(2023, date.today().year+1)]
    keyboard = InlineKeyboardBuilder()
    for year in year_list:
        keyboard.add(InlineKeyboardButton(text=f'{year} ✅' if year == year_cur else f'{year}', callback_data=StatCallBack(
            level=0, text=text, cur_year=year, cur_month=cur_month ).pack()))
   
    return keyboard.adjust(*sizes).as_markup()