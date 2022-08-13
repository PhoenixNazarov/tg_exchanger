from aiogram import Bot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from config import *
from data.local import *

bot = Bot(token = API_TOKEN)

engine = create_engine(SQL_PATH)
session_maker = sessionmaker(bind = engine, autoflush = False)
session_factory = scoped_session(sessionmaker(bind = engine))
