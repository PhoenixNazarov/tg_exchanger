from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import *
from database.models import MessageTransaction
from messages.transactions import *
from share import dp, bot, session_maker


class FSMMessage(StatesGroup):
    write_message = State()


@dp.message_handler(commands = ['mytrans'], state = '*')
async def my_transactions(message: types.Message):
    with session_factory() as session:
        transactions = session.query(Transaction).filter(
            or_(Transaction.merchant_id == message.from_user.id, Transaction.user_id == message.from_user.id)) \
            .filter(or_(Transaction.status == TransStatus.in_stack,
                        Transaction.status == TransStatus.in_exchange,
                        Transaction.status == TransStatus.wait_good_user)).all()

        if len(transactions) == 0:
            return await message.answer(**havenot_transactions)

        for trans in transactions:
            if trans.user_id == message.from_user.id:
                await message.answer(**get_screen_transaction_user(trans))
            else:
                await message.answer(**get_transaction_merchant(trans))


@dp.callback_query_handler(cancel_trans_user_m.filter(), state = '*')
async def del_transaction(query: types.CallbackQuery, callback_data: dict):
    await bot.edit_message_text(**transaction_cancel_a(query.message.text, callback_data['id']),
                                chat_id = query.message.chat.id,
                                message_id = query.message.message_id)


@dp.callback_query_handler(cancel_trans_user_a.filter(), state = '*')
async def del_transaction_a(query: types.CallbackQuery, callback_data: dict):
    with session_maker() as session:
        transaction = session.query(Transaction).get(int(callback_data['id']))

        if int(callback_data['yes']):
            if transaction.status != TransStatus.in_stack:
                await bot.edit_message_text(**get_screen_transaction_user(transaction),
                                            chat_id = query.message.chat.id,
                                            message_id = query.message.message_id)
                return await query.answer(**cant_cancel_transaction)

            transaction.status = TransStatus.canceled
            session.commit()

            await bot.delete_message(chat_id = MERCHANT_CHANNEL, message_id = transaction.merchant_message_id)

        await bot.edit_message_text(**get_screen_transaction_user(transaction),
                                    chat_id = query.message.chat.id,
                                    message_id = query.message.message_id)


@dp.callback_query_handler(transaction_messages.filter(), state = '*')
async def transaction_action(query: types.CallbackQuery, callback_data: dict, state):
    with session_maker() as session:
        transaction: Transaction = session.query(Transaction).get(int(callback_data['id']))

        if callback_data['action'] == TransAction.main:
            await bot.edit_message_text(chat_id = query.from_user.id, message_id = query.message.message_id,
                                        **(get_screen_transaction_user(transaction)
                                           if transaction.user_id == query.from_user.id else
                                           get_transaction_merchant(transaction)))

        elif callback_data['action'] == TransAction.show_messages:
            if len(transaction.messages) == 0:
                return await query.answer(havenot_messages)
            await bot.edit_message_text(chat_id = query.from_user.id, message_id = query.message.message_id, parse_mode=types.ParseMode.MARKDOWN,
                                        **get_transaction_message_history(transaction))

        elif callback_data['action'] == TransAction.write_message:
            await FSMMessage.write_message.set()
            async with state.proxy() as data:
                data['id'] = int(callback_data['id'])
            await bot.send_message(chat_id = query.from_user.id, text = write_transaction_message)

        elif callback_data['action'] == TransAction.cancel:
            pass

        elif callback_data['action'] == TransAction.accept:
            await bot.edit_message_text(chat_id = query.from_user.id, message_id = query.message.message_id,
                                        **accept_status(transaction, transaction.merchant_id == query.from_user.id))


@dp.callback_query_handler(transaction_messages_accept_proof.filter(), state = '*')
async def accept_transaction(query: types.CallbackQuery, callback_data: dict, state):
    with session_maker() as session:
        transaction: Transaction = session.query(Transaction).get(int(callback_data['id']))

        if transaction.merchant_id == query.from_user.id:
            if transaction.status == TransStatus.in_exchange:
                transaction.status = TransStatus.wait_good_user
                session.commit()
                await bot.send_message(chat_id = transaction.user_id, **get_accept_status(transaction, False))
            else:
                await query.answer(cant_accept)
            await bot.edit_message_text(chat_id = query.from_user.id, message_id = query.message.message_id,
                                        **get_transaction_merchant(transaction))

        elif transaction.user_id == query.from_user.id:
            if transaction.status == TransStatus.wait_good_user:
                transaction.status = TransStatus.good_finished
                session.commit()
                await bot.delete_message(chat_id = MERCHANT_CHANNEL, message_id = transaction.merchant_message_id)
                await bot.send_message(chat_id = transaction.merchant_id, **get_accept_status(transaction, True))
            else:
                await query.answer(cant_accept)
            await bot.edit_message_text(chat_id = query.from_user.id, message_id = query.message.message_id,
                                        **get_screen_transaction_user(transaction))

        else:
            await query.answer(cant_accept)


@dp.message_handler(lambda message: message.text not in MAIN_COMMANDS, state = FSMMessage.write_message)
async def write_message(message: types.Message, state):
    async with state.proxy() as data:
        trans_id = data['id']

    with session_maker() as session:
        transaction: Transaction = session.query(Transaction).get(trans_id)

        mes = MessageTransaction()
        mes.text = message.text
        mes.transaction_id = transaction.id

        if transaction.user_id == message.from_user.id:
            mes.from_merchant = False
            await bot.send_message(chat_id = transaction.merchant_id,
                                   **get_transaction_message(transaction, mes))
        else:
            mes.from_merchant = True
            await bot.send_message(chat_id = transaction.user_id,
                                   **get_transaction_message(transaction, mes))
        session.add(mes)
        session.commit()
