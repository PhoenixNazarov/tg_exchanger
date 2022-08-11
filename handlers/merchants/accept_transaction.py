from aiogram import types

from config import *
from database.models.transaction import *
from database.models.merchant import Merchant
from messages.transactions import *
from modules.transactions import merchant_allow_transaction
from share import dp, bot, session_factory


@dp.callback_query_handler(accept_trans_merchant.filter(), state = '*')
async def del_transaction(query: types.CallbackQuery, callback_data: dict):
    with session_factory() as session:
        merchant = session.query(Merchant).get(query.message.chat.id)
        if merchant is None:
            return await query.answer(**not_allow_transaction())

        transaction = session.query(Transaction).get(int(callback_data['id']))
        if not merchant_allow_transaction(transaction, merchant):
            return await query.answer(**not_allow_transaction())

        if bool(callback_data['accept']):
            transaction.status = TransStatus.in_exchange
            transaction.merchant_id = query.from_user.id
            session.commit()

            # merchant channel
            await bot.edit_message_text(chat_id = MERCHANT_CHANNEL, message_id = transaction.merchant_message_id,
                                        **get_transaction_channel(transaction))

            # merchant
            await bot.send_message(chat_id = transaction.merchant_id, **get_screen_transaction_user(transaction))

            # maker
            await bot.send_message(chat_id = transaction.user_id, **get_screen_transaction_user(transaction))
        else:
            pass
