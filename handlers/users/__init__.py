from aiogram import types
from share import dp, bot

from messages.users import *

from . import start_auth


@dp.message_handler(commands=['help', 'start'], state = '*')
async def send_welcome(message: types.Message, state):
    await state.finish()
    await message.answer(**main_screen)

from . import my_transactions
from . import make_transaction


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'del_message', state = '*')
async def delete_cb_message(query: types.CallbackQuery):
    await bot.delete_message(query.message.chat.id, query.message.message_id)


@dp.message_handler(state = None)
async def send_welcome(message: types.Message):
    await message.answer(**main_screen)
