from aiogram import types
from share import dp, IsAdmin, session_maker
from messages.admins import *
from database.models import User, Merchant
from sqlalchemy.sql import exists


@dp.message_handler(IsAdmin(), commands = ['add_merch'], state = '*')
async def add_merchant(message: types.Message):
    merch_id = message.text.split()
    if len(merch_id) != 2:
        return await message.answer(**admin_wrong_count_arguments())

    try:
        merch_id = int(merch_id[1])
    except ValueError:
        return await message.answer(**admin_wrong_id())

    with session_maker() as session:
        if not session.query(exists().where(User.id == merch_id)).scalar():
            return await message.answer(**admin_id_not_found())

        merchant = Merchant(id = merch_id)
        session.add(merchant)
        session.commit()
        await message.answer(**admin_merchant_add(merchant))


@dp.message_handler(IsAdmin(), commands = ['del_merch'], state = '*')
async def add_merchant(message: types.Message):
    merch_id = message.text.split()
    if len(merch_id) != 2:
        return await message.answer(**admin_wrong_count_arguments())

    try:
        merch_id = int(merch_id[1])
    except ValueError:
        return await message.answer(**admin_wrong_id())

    with session_maker() as session:
        if not session.query(exists().where(Merchant.id == merch_id)).scalar():
            return await message.answer(**admin_id_not_found())

        session.delete(session.query(Merchant).get(merch_id))
        session.commit()
        await message.answer(**admin_merchant_del(merch_id))


@dp.message_handler(IsAdmin(), commands = ['list_merch'], state = '*')
async def list_merchant(message: types.Message):
    with session_maker() as session:
        merchants = session.query(Merchant).all()
        for merch in merchants:
            await message.answer(**admin_merchant_list(merch))

