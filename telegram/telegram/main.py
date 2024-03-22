import asyncio
import logging
import sys


from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold


from telegram.backend_requests import API
from telegram.routers.register import register_router
from telegram.routers.subscribe import (
    subscribe_router,
    unsubscribe_router,
    subscriptions_router,
)
from telegram.settings import API_KEY, TOKEN

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    api = API(API_KEY)
    response = api.get_user(message.from_user.id)
    if not response:
        await message.answer("Something went wrong!")
        return
    data = response.json()
    if response.status != 200:
        await message.answer(f"{data.get('detail')}")
        return
    await message.answer(f"Hello, {hbold(data.get('email'))}!")


@dp.message(Command("trigger"))
async def command_trigger_analysis_handler(message: Message) -> None:
    api = API(API_KEY)
    response = api.get_user(message.from_user.id)
    if not response:
        await message.answer("Something went wrong!")
        return
    data = response.json()
    if response.status != 200:
        await message.answer(f"{data.get('detail')}")
        return

    api.trigger_analysis(message.from_user.id)
    await message.answer("Stock analysis done")


async def main() -> None:
    if not TOKEN:
        logging.error("No token provided!")
        sys.exit(1)
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    dp.include_router(register_router)
    dp.include_router(subscribe_router)
    dp.include_router(unsubscribe_router)
    dp.include_router(subscriptions_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
