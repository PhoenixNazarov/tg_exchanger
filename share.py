from aiogram import Bot, Dispatcher, executor, md, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())


engine = create_engine(SQL_PATH)
session_maker = sessionmaker(bind = engine, autoflush=False)
session_factory = scoped_session(sessionmaker(bind = engine))

