from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import MERCHANT_CHANNEL
from messages.transactions import *
from messages.users import *
from share import dp, bot, session_maker


class FSMTransaction(StatesGroup):
    have_currency = State()
    get_currency = State()
    amount = State()
    rate = State()


@dp.message_handler(commands = ['newtrans'], state = '*')
async def trans_start(message: types.Message, state):
    await state.finish()
    await FSMTransaction.have_currency.set()
    await message.answer(**make_transaction_have_currency)


@dp.message_handler(state = FSMTransaction.have_currency)
async def load_buy(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == Currency.BAT:
            data['have_currency'] = Currency.BAT
            await message.answer(**make_transaction_get_fiat_currency)
            await FSMTransaction.next()
        elif message.text in fiat_currency:
            data['have_currency'] = message.text
            data['get_currency'] = Currency.BAT
            await message.answer(**make_transaction_amount(message.text))
            await FSMTransaction.amount.set()
        else:
            await message.answer(**make_transaction_have_currency)


@dp.message_handler(state = FSMTransaction.get_currency)
async def load_currency(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text not in fiat_currency:
            return await message.answer(**make_transaction_get_fiat_currency)
        data['get_currency'] = message.text
        await message.answer(**make_transaction_amount(data['have_currency']))
    await FSMTransaction.next()


def correct_number(number: str):
    try:
        number = float(number.replace(',', '.'))
        return number * 100 == int(number * 100)
    except ValueError:
        return False


@dp.message_handler(state = FSMTransaction.amount)
async def load_amount(message: types.Message, state: FSMContext):
    if not correct_number(message.text):
        return await message.answer(**make_transaction_incorrect_number)

    async with state.proxy() as data:
        data['amount'] = float(message.text.replace(',', '.'))
        await message.answer(**make_transaction_rate(data['have_currency'], data['get_currency']))
    await FSMTransaction.next()


@dp.message_handler(state = FSMTransaction.rate)
async def load_rate(message: types.Message, state: FSMContext):
    if not correct_number(message.text):
        return await message.answer(**make_transaction_incorrect_number)

    async with state.proxy() as data:
        data['rate'] = float(message.text.replace(',', '.'))
        await message.answer(**make_transaction_show(*dict(data).values()))
    await state.finish()


@dp.callback_query_handler(make_transaction_cd.filter(), state = '*')
async def public_transaction(query: types.CallbackQuery, callback_data: dict):
    callback_data['amount'] = float(callback_data['amount'])
    callback_data['rate'] = float(callback_data['rate'])
    callback_data.pop('@')

    transaction: Transaction
    with session_maker() as session:
        transaction = Transaction(**callback_data, auth_user = session.query(User).get(query.from_user.id).auth)
        transaction.user_id = query.from_user.id
        session.add(transaction)
        session.commit()
        transaction = session.query(Transaction).get(transaction.id)

        await bot.edit_message_text(**get_screen_transaction_user(transaction), chat_id = query.message.chat.id,
                                    message_id = query.message.message_id)

        merchant_message = await bot.send_message(chat_id = MERCHANT_CHANNEL, **get_transaction_channel(transaction))
        transaction.merchant_message_id = merchant_message.message_id
        session.commit()
