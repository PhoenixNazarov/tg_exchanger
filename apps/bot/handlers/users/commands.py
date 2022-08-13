from aiogram import types, Dispatcher

from apps.bot.messages.users import *
from share import bot


async def send_welcome(message: types.Message, state):
    await state.finish()
    await message.answer(**main_screen)


async def delete_cb_message(query: types.CallbackQuery):
    await bot.delete_message(query.message.chat.id, query.message.message_id)


def register_handlers_commands(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands = ['help', 'start'], state = '*')
    dp.register_callback_query_handler(delete_cb_message, lambda callback_query: callback_query.data == 'del_message',
                                       state = '*')
