from aiogram.dispatcher.filters import Filter
from aiogram import types
from config import ADMINS


class IsAdmin(Filter):
    key = "is_admin"

    async def check(self, message: types.Message):
        return message.from_user.id in ADMINS


def bind_filters(dp):
    dp.bind_filter(IsAdmin)