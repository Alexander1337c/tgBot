import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
from database.engine import create_db, drop_db, session_maker
from common.bot_commands_private import private
from handlers import card_handlers, user_private, admin_handlers
from middlewares.db import DataBaseSession


# ALLOWED_UPDATE = ['message', 'edited_message']

bot = Bot(token=os.getenv('TOKEN'),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = [572021120]

dp = Dispatcher()
dp.include_router(user_private.user_private_router)
dp.include_router(card_handlers.add_card_private_router)
dp.include_router(admin_handlers.admin_router)

async def on_startup(bot):

    # await drop_db()

    await create_db()

async def on_shutdown(bot):
    print('Бот лежит')

async def main():
    await create_db()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats() )
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
