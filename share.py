from aiogram import Bot, Dispatcher, executor, md, types
from aiogram.dispatcher.filters import Filter
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from config import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


# 30073
storage = RedisStorage2('localhost', 49155, password = 'redispw')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage = storage)


class IsAdmin(Filter):
    key = "is_admin"

    async def check(self, message: types.Message):
        return message.from_user.id in ADMINS


dp.bind_filter(IsAdmin)


engine = create_engine(SQL_PATH)
session_maker = sessionmaker(bind = engine, autoflush=False)
session_factory = scoped_session(sessionmaker(bind = engine))
