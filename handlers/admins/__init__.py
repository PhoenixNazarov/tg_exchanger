from aiogram import types
from share import dp, IsAdmin
from messages.admins import *


@dp.message_handler(IsAdmin(), commands = ['admin_help'], state = '*')
async def admin_help(message: types.Message):
    await message.answer(**help_admin())


from . import commands
