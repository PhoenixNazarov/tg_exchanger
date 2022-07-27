from aiogram import types

from config import *
from database.models.transaction import *
from messages.transactions import *
from share import dp, bot, session_factory


@dp.callback_query_handler(accept_trans_merchant.filter(), state = '*')
async def del_transaction(query: types.CallbackQuery, callback_data: dict):
    # todo check sum of the trans and limit merchant
    if False:
        await query.answer("qweqwe")

    with session_factory() as session:
        transaction = session.query(Transaction).get(int(callback_data['id']))
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
