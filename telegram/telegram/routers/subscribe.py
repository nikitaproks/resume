import logging

import yfinance as yf

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder


from telegram.backend_requests import API, authorize
from telegram.settings import API_KEY


logger = logging.getLogger(__name__)


class Subscribe(StatesGroup):
    ticker = State()
    period = State()
    interval = State()


class Unsubscribe(StatesGroup):
    ticker = State()


def validate_ticker(text: str) -> yf.Ticker | None:
    ticker = yf.Ticker(text.upper())
    history = ticker.history(period="1d", interval="1d")
    if len(history) == 0:
        return
    return ticker


subscribe_router = Router()
unsubscribe_router = Router()
subscriptions_router = Router()


# Subscriptions
@subscriptions_router.message(Command("subscriptions"))
async def command_subscriptions(message: Message) -> None:
    api = API(API_KEY)
    if not authorize(api, message):
        await message.answer(
            "You are not registered!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    response = api.list_subscriptions(
        message.from_user.id,
    )
    if not response or response.status != 200:
        await message.answer(
            "Something went wrong!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if len(response.json()) == 0:
        await message.answer(
            "You have no subscriptions.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    message_text = "Your subscriptions:"
    for subscription in response.json():
        message_text += f"\n    - {subscription['stock']['name']} {subscription['stock']['ticker']}"

    await message.answer(
        message_text,
        reply_markup=ReplyKeyboardRemove(),
    )


# Subscribe


@subscribe_router.message(Command("cancel"))
@subscribe_router.message(F.text.casefold() == "cancel")
async def cancel_subscribe(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@subscribe_router.message(Command("subscribe"))
async def command_subscribe(message: Message, state: FSMContext) -> None:
    api = API(API_KEY)
    if not authorize(api, message):
        await message.answer(
            "You are not registered!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    await state.set_state(Subscribe.ticker)
    await message.answer(
        "Enter ticker:",
        reply_markup=ReplyKeyboardRemove(),
    )


@subscribe_router.message(
    lambda message: not message.text.startswith("/"), Subscribe.ticker
)
async def set_ticker(message: Message, state: FSMContext) -> None:
    if not (ticker := validate_ticker(message.text)):
        await message.answer(
            f"Ticker {message.text} is not available. Please try another one:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await state.update_data(ticker=ticker)
    await state.set_state(Subscribe.period)

    builder = InlineKeyboardBuilder()

    periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
    for period in periods:
        builder.button(
            text=period,
            callback_data=period,
        )
    await message.answer(
        "Choose period:",
        reply_markup=builder.as_markup(),
    )


@subscribe_router.message(
    lambda message: not message.text.startswith("/"), Subscribe.ticker
)
async def set_period(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(period=query.data)
    await state.set_state(Subscribe.interval)

    builder = InlineKeyboardBuilder()
    intervals = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
    for interval in intervals:
        builder.button(
            text=interval,
            callback_data=interval,
        )
    await query.message.answer(
        "Choose interval:",
        reply_markup=builder.as_markup(),
    )


@subscribe_router.message(
    lambda message: not message.text.startswith("/"), Subscribe.interval
)
async def set_interval_and_submit(
    query: CallbackQuery, state: FSMContext
) -> None:
    api = API(API_KEY)
    data = await state.get_data()
    ticker: yf.Ticker | None = data.get("ticker")
    if not ticker:
        await query.message.answer(
            "Something went wrong!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    response = api.subscribe_stock(
        query.from_user.id,
        ticker.ticker,
        ticker.info["shortName"],
        data.get("period"),
        data.get("interval"),
    )
    if not response or response.status != 201:
        await query.message.answer(
            "Something went wrong!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    await state.clear()
    await query.message.answer(
        f"Subscribed to ticker {ticker.ticker}!",
        reply_markup=ReplyKeyboardRemove(),
    )


# Unsubscribe
@unsubscribe_router.message(Command("unsubscribe"))
async def command_unsubscribe(message: Message, state: FSMContext) -> None:
    api = API(API_KEY)
    if not authorize(api, message):
        await message.answer(
            "You are not registered!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    response = api.list_subscriptions(
        message.from_user.id,
    )
    if not response or response.status != 200:
        await message.answer(
            "Something went wrong!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    if len(response.json()) == 0:
        await message.answer(
            "You have no subscriptions.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    builder = InlineKeyboardBuilder()
    for subscription in response.json():
        builder.button(
            text=subscription["stock"]["ticker"],
            callback_data=subscription["stock"]["ticker"],
        )
    await state.set_state(Unsubscribe.ticker)
    await message.answer(
        "Choose ticker:",
        reply_markup=builder.as_markup(),
    )


@unsubscribe_router.message(Command("cancel"))
@unsubscribe_router.message(F.text.casefold() == "cancel")
async def cancel_unsubscribe(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@unsubscribe_router.callback_query(Unsubscribe.ticker)
async def unsubscribe(query: CallbackQuery, state: FSMContext) -> None:
    api = API(API_KEY)
    response = api.unsubscribe_stock(
        query.from_user.id,
        query.data,
    )
    if not response or response.status != 200:
        await query.message.answer(
            "Something went wrong!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    await state.update_data(ticker=query.data)
    await state.clear()
    await query.message.answer(
        f"Unsubscribed from ticker {query.data}!",
        reply_markup=ReplyKeyboardRemove(),
    )
