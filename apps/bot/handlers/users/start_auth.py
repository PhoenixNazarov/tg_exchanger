from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from sqlalchemy.sql import exists

from database.models import User
from apps.bot.messages.users import *
from share import session_factory


def check_register(message):
    with session_factory() as session:
        return session.query(exists().where(User.id == message.from_user.id)).scalar()


class FSMRegistration(StatesGroup):
    get_username = State()
    get_telephone = State()


async def send_welcome(message: types.Message, state):
    await FSMRegistration.get_username.set()
    if message.from_user.username is None:
        return await message.answer(**start_screen_username_not)
    with session_factory() as session:
        user = User()
        user.id = message.from_user.id
        user.username = message.from_user.username
        user.first_name = message.from_user.first_name
        user.last_name = message.from_user.last_name
        user.language = message.from_user.language_code
        user.is_premium = message.from_user.is_premium
        session.add(user)
        session.commit()
    await FSMRegistration.get_telephone.set()
    await message.answer(**start_screen_allow)


async def send_welcome_final(message: types.Message, state):
    if message.contact is None:
        return await message.answer(**start_screen_allow)

    with session_factory() as session:
        user = session.query(User).get(message.contact.user_id)
        user.phone = message.contact.phone_number
        session.commit()

    await state.finish()
    await message.answer(**main_screen, reply_markup = types.ReplyKeyboardRemove())


def register_handlers_auth(dp: Dispatcher):
    dp.register_message_handler(send_welcome, state = FSMRegistration.get_username)
    dp.register_message_handler(send_welcome, lambda message: not check_register(message), commands = ['start'],
                                state = '*')
    dp.register_message_handler(send_welcome_final, content_types = ['contact'], state = FSMRegistration.get_telephone)
