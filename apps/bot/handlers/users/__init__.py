from aiogram import types, Dispatcher

from apps.bot.messages.users import *

from .start_auth import register_handlers_auth
from .commands import register_handlers_commands
from .my_transactions import register_handlers_my_transaction, register_handler_my_transaction
from .make_transaction import register_handlers_make_transaction, register_handler_make_transaction


async def send_welcome(message: types.Message):
    await message.answer(**main_screen)


def register_handlers_user(dp: Dispatcher):
    register_handlers_auth(dp)
    register_handlers_commands(dp)
    register_handler_my_transaction(dp)
    register_handler_make_transaction(dp)

    register_handlers_my_transaction(dp)
    register_handlers_make_transaction(dp)

    dp.register_message_handler(send_welcome, state = "*")

