from aiogram import types
from share import dp, IsAdmin, session_maker
from messages.admins import *
from database.models import User, Merchant, MerchantCommission
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
        merchant_commission = MerchantCommission(id = merch_id)
        session.add(merchant)
        session.add(merchant_commission)
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
        session.delete(session.query(MerchantCommission).get(merch_id))
        session.commit()
        await message.answer(**admin_merchant_del(merch_id))


@dp.message_handler(IsAdmin(), commands = ['list_merch'], state = '*')
async def list_merchant(message: types.Message):
    with session_maker() as session:
        merchants = session.query(Merchant).all()
        for merch in merchants:
            await message.answer(**admin_merchant_list(merch))


@dp.message_handler(IsAdmin(), commands = ['set_limit_amount'], state = '*')
async def set_limit_amount(message: types.Message):
    args = message.text.split()
    if len(args) != 3:
        return await message.answer(**admin_wrong_count_arguments())

    try:
        merch_id = int(args[1])
        value = float(args[2])
    except ValueError:
        return await message.answer(**admin_wrong_id())

    with session_maker() as session:
        merchant = session.query(Merchant).get(merch_id)
        if merchant is None:
            return await message.answer(**admin_id_not_found())

        merchant.allow_max_amount = value
        session.commit()
        await message.answer(**admin_merchant_list(merchant))


@dp.message_handler(IsAdmin(), commands = ['set_limit_amount'], state = '*')
async def set_accumulated_commission(message: types.Message):
    args = message.text.split()
    if not (2 <= len(args) <= 4):
        return await message.answer(**admin_wrong_count_arguments())

    try:
        merch_id = int(args[1])
    except ValueError:
        return await message.answer(**admin_wrong_id())

    with session_maker() as session:
        merchant: Merchant = session.query(Merchant).get(merch_id)
        if merchant is None:
            return await message.answer(**admin_id_not_found())

        currency = None
        value = 0
        if len(args) > 2:
            currency = args[2]
            if currency not in ['usd', 'rub', 'thb']:
                return await message.answer(**admin_wrong_currency())

        if len(args) > 3:
            try:
                value = float(args[3])
            except ValueError:
                return await message.answer(**admin_wrong_count())

        match currency, value:
            case None, _:
                merchant.accumulated_commission.usd = 0
                merchant.accumulated_commission.thb = 0
                merchant.accumulated_commission.rub = 0
            case 'rub', v:
                merchant.accumulated_commission.rub = v
            case 'usd', v:
                merchant.accumulated_commission.usd = v
            case 'thb', v:
                merchant.accumulated_commission.thb = v

        session.commit()
        await message.answer(**admin_merchant_list(merchant))
