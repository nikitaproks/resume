import logging

from pydantic import BaseModel, EmailStr

from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from telegram.backend_requests import API
from telegram.settings import API_KEY


logger = logging.getLogger(__name__)


class Email(BaseModel):
    email: EmailStr


class Register(StatesGroup):
    invite_code = State()
    email = State()


def validate_email(text: str) -> str | None:
    try:
        validator = Email(email=text)
        return validator.email
    except:
        return None


register_router = Router()


@register_router.message(Command("cancel"))
@register_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
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


@register_router.message(Command("register"))
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Register.invite_code)
    await message.answer(
        "Enter invite code:",
        reply_markup=ReplyKeyboardRemove(),
    )


@register_router.message(Register.invite_code)
async def process_invite_code(message: Message, state: FSMContext) -> None:
    await state.update_data(invite_code=message.text)
    await state.set_state(Register.email)
    await message.answer(
        "Enter email address:",
        reply_markup=ReplyKeyboardRemove(),
    )


@register_router.message(Register.email)
async def process_name(message: Message, state: FSMContext) -> None:
    if not (email := validate_email(message.text)):
        await message.answer(
            "Email is not valid. Please try again:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    api = API(API_KEY)
    invite_code = await state.get_data()
    response = api.register_user(
        message.from_user.id, email, invite_code.get("invite_code")
    )
    if not response:
        await message.answer(
            "Something went wrong!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return
    # TODO: Show error if invide code is invalid
    if response.status == 409:
        await message.answer(
            "This user is already registered!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if not response.status == 201:
        await message.answer(
            "Something went wrong!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await state.update_data(email=message.text)
    await state.clear()
    await message.answer(
        "User registered successfully!",
        reply_markup=ReplyKeyboardRemove(),
    )
