from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from apps.bot.messages.transactions import *
from share import bot, session_maker
from database.models.transaction_requisits import *


class FSMTransaction(StatesGroup):
    have_currency = State()
    get_currency = State()
    amount = State()
    rate = State()

    type_get_thb = State()


class FSMCash(StatesGroup):
    town = State()
    region = State()


class FSMBank(StatesGroup):
    bank = State()
    number = State()
    name = State()


async def trans_start(message: types.Message, state):
    await state.finish()
    await FSMTransaction.have_currency.set()
    await message.answer(**make_transaction_have_currency)


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


async def load_amount(message: types.Message, state: FSMContext):
    if not correct_number(message.text):
        return await message.answer(**make_transaction_incorrect_number)

    async with state.proxy() as data:
        data['amount'] = float(message.text.replace(',', '.'))
        await message.answer(**make_transaction_rate(data['have_currency'], data['get_currency']))
    await FSMTransaction.next()


async def send_pre_transaction(message: types.Message, callback_data):
    with session_maker() as session:
        user = session.query(User).get(message.from_user.id)
        trans: TransactionModerate = TransactionModerate(
            amount = callback_data['amount'],
            have_currency = callback_data['have_currency'],
            get_currency = callback_data['get_currency'],
            rate = callback_data['rate'],
            auth_user = user.auth
        )
        trans.user_id = user.id
        trans.get_thb_type = callback_data['type_get_thb']
        if trans.get_thb_type == TransGet.cash:
            trans.option1 = callback_data['town']
            trans.option2 = callback_data['region']
        elif trans.get_thb_type == TransGet.atm_machine:
            pass
        elif trans.get_thb_type == TransGet.bank_balance:
            trans.option1 = callback_data['bank']
            trans.option2 = callback_data['number']
            trans.option3 = callback_data['name']

        session.add(trans)
        session.commit()
        await message.answer(**make_transaction_show(trans))


async def load_rate(message: types.Message, state: FSMContext):
    if not correct_number(message.text):
        return await message.answer(**make_transaction_incorrect_number)

    async with state.proxy() as data:
        data['rate'] = float(message.text.replace(',', '.'))

        if data['have_currency'] == Currency.BAT:
            data['type_get_thb'] = TransGet.none
            await send_pre_transaction(message, dict(data))
        else:
            await message.answer(**make_transaction_get_type_thb())
            await FSMTransaction.next()


async def load_type_get_thb(message: types.Message, state: FSMContext):
    if message.text not in transaction_get.values():
        return await message.answer(**make_transaction_get_type_thb())

    async with state.proxy() as data:
        for _type in transaction_get:
            if transaction_get[_type] == message.text:
                data['type_get_thb'] = _type

        if data['type_get_thb'] == TransGet.cash:
            await FSMCash.town.set()
            await message.answer(**make_transaction_town())

        elif data['type_get_thb'] == TransGet.atm_machine:
            await message.answer(**make_transaction_end())
            await send_pre_transaction(message, dict(data))

        elif data['type_get_thb'] == TransGet.bank_balance:
            await FSMBank.bank.set()
            return await message.answer(**make_transaction_bank())


async def load_town(message: types.Message, state: FSMContext):
    if message.text not in config.TOWNS:
        return await message.answer(**make_transaction_town())

    async with state.proxy() as data:
        data['town'] = message.text

    await FSMCash.next()
    await message.answer(**make_transaction_region(message.text))


async def load_region(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text not in config.TOWNS[data['town']]:
            return await message.answer(**make_transaction_region(data['town']))
        data['region'] = message.text

        await message.answer(**make_transaction_end())
        await send_pre_transaction(message, dict(data))
    await state.finish()


async def load_bank(message: types.Message, state: FSMContext):
    if message.text not in config.BANKS:
        return await message.answer(**make_transaction_bank())

    async with state.proxy() as data:
        data['bank'] = message.text

    await message.answer(**make_transaction_number())
    await FSMBank.next()


async def load_number(message: types.Message, state: FSMContext):
    if len(message.text) != 9:
        return await message.answer(**make_transaction_number())
    try:
        int(message.text)
    except ValueError:
        return await message.answer(**make_transaction_number())

    async with state.proxy() as data:
        data['number'] = message.text

    await message.answer(**make_transaction_name())
    await FSMBank.next()


async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

        await message.answer(**make_transaction_end())
        await send_pre_transaction(message, dict(data))
        await state.finish()


async def public_transaction(query: types.CallbackQuery, callback_data: dict):
    with session_maker() as session:
        transaction_moderate: TransactionModerate = session.query(TransactionModerate).get(callback_data['id'])

        if int(callback_data['public']):
            transaction: Transaction = Transaction()
            transaction.user_id = query.from_user.id
            transaction.have_amount = transaction_moderate.have_amount
            transaction.have_currency = transaction_moderate.have_currency
            transaction.get_amount = transaction_moderate.get_amount
            transaction.get_currency = transaction_moderate.get_currency
            transaction.rate = transaction_moderate.rate

            transaction.commission_user = transaction_moderate.commission_user
            transaction.commission_merchant = transaction_moderate.commission_merchant
            transaction.get_thb_type = transaction_moderate.get_thb_type

            session.add(transaction)
            session.commit()
            if transaction.get_thb_type == TransGet.cash:
                reqCash = RequisitesCash()
                reqCash.transaction_id = transaction.id
                reqCash.town = transaction_moderate.option1
                reqCash.region = transaction_moderate.option2
                session.add(reqCash)
                session.commit()
            elif transaction.get_thb_type == TransGet.bank_balance:
                reqBank = RequisitesBankBalance()
                reqBank.transaction_id = transaction.id
                reqBank.bank_name = transaction_moderate.option1
                reqBank.number = transaction_moderate.option2
                reqBank.name = transaction_moderate.option3
                session.add(reqBank)
                session.commit()

            await bot.edit_message_text(**get_transaction_user(transaction), chat_id = query.message.chat.id,
                                        message_id = query.message.message_id)

            merchant_message = await bot.send_message(chat_id = MERCHANT_CHANNEL, **get_transaction_channel(transaction))
            transaction.merchant_message_id = merchant_message.message_id
            session.commit()
        else:
            await bot.delete_message(chat_id = query.from_user.id, message_id = query.message.message_id)

        session.delete(transaction_moderate)


def register_handler_make_transaction(dp: Dispatcher):
    dp.register_message_handler(trans_start, commands = ['newtrans'], state = '*')


def register_handlers_make_transaction(dp: Dispatcher):
    dp.register_message_handler(load_buy, state = FSMTransaction.have_currency)
    dp.register_message_handler(load_currency, state = FSMTransaction.get_currency)
    dp.register_message_handler(load_amount, state = FSMTransaction.amount)
    dp.register_message_handler(load_rate, state = FSMTransaction.rate)
    dp.register_message_handler(load_type_get_thb, state = FSMTransaction.type_get_thb)

    dp.register_message_handler(load_town, state = FSMCash.town)
    dp.register_message_handler(load_region, state = FSMCash.region)

    dp.register_message_handler(load_bank, state = FSMBank.bank)
    dp.register_message_handler(load_number, state = FSMBank.number)
    dp.register_message_handler(load_name, state = FSMBank.name)

    dp.register_callback_query_handler(public_transaction, make_transaction_cd.filter(), state = '*')

