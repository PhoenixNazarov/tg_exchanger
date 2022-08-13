from aiogram import types, Dispatcher

from apps.bot.messages.transactions import *
from database.transactions import merchant_allow_transaction
from share import bot, session_factory


async def accept_transaction(query: types.CallbackQuery, callback_data: dict):
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
            await bot.send_message(chat_id = transaction.merchant_id, **get_transaction_user(transaction))

            # maker
            await bot.send_message(chat_id = transaction.user_id, **get_transaction_user(transaction))
        else:
            pass


def register_handlers_accept_transaction(dp: Dispatcher):
    dp.register_callback_query_handler(accept_transaction, accept_trans_merchant.filter(), state = '*')