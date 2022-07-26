from aiogram import types
from sqlalchemy import or_
from messages.transactions import *
from share import dp, bot, session_factory
from config import *


@dp.message_handler(commands = ['mytrans'], state = '*')
async def my_transactions(message: types.Message):
    with session_factory() as session:
        transactions = session.query(Transaction).filter(or_(Transaction.status == TransStatus.in_stack,
                                                             Transaction.status == TransStatus.in_exchange)).all()

        if len(transactions) == 0:
            return await message.answer(**havenot_transactions)

        for trans in transactions:
            await message.answer(**get_screen_transaction_user(trans))


@dp.callback_query_handler(cancel_trans_user_m.filter(), state = '*')
async def del_transaction(query: types.CallbackQuery, callback_data: dict):
    await bot.edit_message_text(**transaction_cancel_a(query.message.text, callback_data['id']),
                                chat_id = query.message.chat.id,
                                message_id = query.message.message_id)


@dp.callback_query_handler(cancel_trans_user_a.filter(), state = '*')
async def del_transaction_a(query: types.CallbackQuery, callback_data: dict):
    with session_factory() as session:
        transaction = session.query(Transaction).get(int(callback_data['id']))
        await bot.edit_message_text(**get_screen_transaction_user(transaction),
                                    chat_id = query.message.chat.id,
                                    message_id = query.message.message_id)

        if int(callback_data['yes']):
            if transaction.status != TransStatus.in_stack:
                return await query.answer(**cant_cancel_transaction)

            transaction.status = TransStatus.canceled
            session.commit()

            await bot.delete_message(chat_id = MERCHANT_CHANNEL, message_id = transaction.merchant_message_id)
