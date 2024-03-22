import logging

import yfinance as yf

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from telegram.backend_requests import API
from telegram.settings import API_KEY
from telegram.backend_requests import authorize

logger = logging.getLogger(__name__)


def validate_ticker(text: str) -> yf.Ticker | None:
    ticker = yf.Ticker(text.upper())
    history = ticker.history(period="1d", interval="1d")
    if len(history) == 0:
        return
    return ticker


trigger_router = Router()
updates_deactivation_router = Router()


@trigger_router.message(Command("trigger"))
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


# Subscriptions
@updates_deactivation_router.message(Command("deactivate"))
async def command_deactivate_updates(message: Message) -> None:
    api = API(API_KEY)
    if not authorize(api, message):
        await message.answer(
            "You are not registered!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    response = api.change_updates_status(message.from_user.id, 0)

    if response.status != 200:
        await message.answer(response.json())
        return

    await message.answer("Successfully deactivated updates")


@updates_deactivation_router.message(Command("activate"))
async def command_activate_updates(message: Message) -> None:
    api = API(API_KEY)
    if not authorize(api, message):
        await message.answer(
            "You are not registered!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    response = api.change_updates_status(message.from_user.id, 1)

    if response.status != 200:
        await message.answer(response.json())
        return

    await message.answer("Successfully deactivated updates")
