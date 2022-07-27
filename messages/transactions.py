from strenum import StrEnum

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from sqlalchemy import or_
import aiogram.utils.markdown as fmt

from database.models import Transaction, User
from database.models.transaction import TransStatus
from database.models.transaction import get_russian_status
from share import session_factory

# MERCHANT CHANNEL
accept_trans_merchant = CallbackData('mtrans', 'id', 'accept', 'ban')


def get_transaction_channel(transaction: Transaction):
    if transaction.status == TransStatus.in_stack:
        return get_transaction_merchant_in_stack(transaction)
    elif transaction.status == TransStatus.in_exchange:
        return get_transaction_merchant_in_exchange(transaction)


def get_transaction_merchant_in_stack(transaction: Transaction):
    with session_factory() as session:
        user = session.query(User).get(transaction.user_id)

    return {
        'text': f'Заявка #{transaction.id}'
                f'\n🤝 Получаете: {transaction.have_amount} {transaction.have_currency}'
                f'\n🤝 Отдаёте: {transaction.get_amount} {transaction.get_currency}'
        # f'\n💸 Комиссия пользователя: {transaction.commission_user} {transaction.get_currency}'
                f'\n💸 Комиссия мерчанта: {transaction.commission_merchant} {transaction.have_currency}'
                f'\n📉 Курс: {transaction.rate}',
        # f'\n' \
        # f'\n👔 Пользователь: @{user.username}' \
        # f'\n📱: {user.phone}' \
        # f'\n🏁: {user.good_transactions}'
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('✅ Принять',
                                 callback_data = accept_trans_merchant.new(id = transaction.id, accept = 1,
                                                                           ban = 0)),
            InlineKeyboardButton('❌ Пожаловаться',
                                 callback_data = accept_trans_merchant.new(id = transaction.id, accept = 0,
                                                                           ban = 1)))

    }


def get_transaction_merchant_in_exchange(transaction: Transaction):
    with session_factory() as session:
        user = session.query(User).get(transaction.merchant_id)
        return {
            'text': f'Заявка #{transaction.id}'
                    f'\n🤝 Получаете: {transaction.have_amount} {transaction.have_currency}'
                    f'\n🤝 Отдаёте: {transaction.get_amount} {transaction.get_currency}'
            # f'\n💸 Комиссия пользователя: {transaction.commission_user} {transaction.get_currency}'
                    f'\n💸 Комиссия мерчанта: {transaction.commission_merchant} {transaction.have_currency}'
                    f'\n📉 Курс: {transaction.rate}'
                    f'\n👨‍💼 Мерчант: @{user.username}'
            # f'\n' \
            # f'\n👔 Пользователь: @{user.username}' \
            # f'\n📱: {user.phone}' \
            # f'\n🏁: {user.good_transactions}'\
        }


# MERCHANT
def get_transaction_merchant(transaction):
    if transaction.status == TransStatus.in_exchange:
        return get_transaction_merchant_in_exc(transaction)
    elif transaction.status == TransStatus.wait_good_user:
        return get_transaction_merchant_in_exc(transaction)


def get_transaction_merchant_in_exc(transaction: Transaction):
    return {
        'text': f'Заявка #{transaction.id}'
                f'\n🤝 Получаете: {transaction.have_amount} {transaction.have_currency}'
                f'\n🤝 Отдаёте: {transaction.get_amount} {transaction.get_currency}'
        # f'\n💸 Комиссия пользователя: {transaction.commission_user} {transaction.get_currency}'
                f'\n💸 Комиссия мерчанта: {transaction.commission_merchant} {transaction.have_currency}'
                f'\n📉 Курс: {transaction.rate}',
        'reply_markup': get_transaction_keyboard_main(transaction, True)
    }


# MAKER
def get_screen_transaction_user(transaction: Transaction):
    if transaction.status == TransStatus.in_stack:
        return {
            'text': get_transaction_user(transaction),
            'reply_markup': get_transaction_keyboard_cancel(transaction)
        }
    elif transaction.status == TransStatus.in_exchange:
        return get_transaction_user_in_exchange(transaction)
    elif transaction.status == TransStatus.wait_good_user:
        return get_transaction_user_in_exchange(transaction)
    elif transaction.status == TransStatus.canceled:
        return {
            'text': get_transaction_user(transaction)
        }


def get_transaction_user(transaction: Transaction):
    # f'\n💸 Комиссия: {transaction.commission_user} {transaction.get_currency}' \
    text = f'Заявка #{transaction.id}' \
           f'\n🤝 Отдаёте: {transaction.have_amount} {transaction.have_currency}' \
           f'\n🤝 Получаете: {transaction.get_amount} {transaction.get_currency}' \
           f'\n📉 Курс: {transaction.rate}' \
           f'\n👔 Статус: {get_russian_status[transaction.status]}'
    if transaction.status == TransStatus.in_stack:
        position = 0
        with session_factory() as session:
            all_models = session.query(Transaction).filter(Transaction.have_currency == transaction.have_currency) \
                .filter(Transaction.get_currency == transaction.get_currency).filter(
                or_(Transaction.status == TransStatus.in_stack,
                    Transaction.status == TransStatus.in_exchange))
            for trans in all_models:
                position += 1
                if trans.id == transaction.id:
                    break
        text += f"\n🥉 Место в очереди: {position}"

    return text


def get_transaction_user_in_exchange(transaction: Transaction):
    text = f'Заявка #{transaction.id}' \
           f'\n🤝 Отдаёте: {transaction.have_amount} {transaction.have_currency}' \
           f'\n🤝 Получаете: {transaction.get_amount} {transaction.get_currency}' \
           f'\n📉 Курс: {transaction.rate}' \
           f'\n👔 Статус: {get_russian_status[transaction.status]}'
    return {
        'text': text,
        'reply_markup': get_transaction_keyboard_main(transaction)
    }


havenot_transactions = {
    'text': 'У вас нет активных заявок.'
            '\nДля создания заявки напишите /newtrans'
}

cancel_trans_user_m = CallbackData('canceltrans', 'id')


def get_transaction_keyboard_cancel(transaction: Transaction):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton('❌ Отменить', callback_data = cancel_trans_user_m.new(id = transaction.id)))


cancel_trans_user_a = CallbackData('canceltransa', 'id', 'yes', 'no')


def transaction_cancel_a(text, trans_id):
    return {
        'text': f'Вы уверены, что хотите удалить данную заявку:\n{text}',
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('✅ Да', callback_data = cancel_trans_user_a.new(id = trans_id, yes = 1, no = 0)),
            InlineKeyboardButton('❌ Нет', callback_data = cancel_trans_user_a.new(id = trans_id, yes = 0, no = 1))
        )}


cant_cancel_transaction = {
    'text': 'Нельзя отменить данную транкзакцию'
}


class TransAction(StrEnum):
    main = 'main'
    write_message = 'write_message'
    show_messages = 'show_messages'
    accept = 'accept'
    cancel = 'cancel'


transaction_messages = CallbackData('trans_in_exc', 'id', 'action')
transaction_messages_cancel_proof = CallbackData('trans_cancel_p', 'id', 'proof')
transaction_messages_accept_proof = CallbackData('trans_accept_p', 'id', 'proof')


def get_transaction_keyboard_main(transaction: Transaction, merchant=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('📩 Написать сообщение',
                             callback_data = transaction_messages.new(id = transaction.id,
                                                                      action = TransAction.write_message)),
        InlineKeyboardButton('✉️ История сообщений',
                             callback_data = transaction_messages.new(id = transaction.id,
                                                                      action = TransAction.show_messages)))

    if (merchant and transaction.status == TransStatus.in_exchange) or (
            not merchant and transaction.status == TransStatus.wait_good_user):
        keyboard.row(
            InlineKeyboardButton('✅ Подтвердить',
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.accept)),
            InlineKeyboardButton('⛔ Пожаловаться',
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.cancel)))
    else:
        keyboard.row(
            InlineKeyboardButton('⛔ Пожаловаться',
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.cancel)))
    return keyboard


# MESSAGES
havenot_messages = 'Не найдено сообщений'
write_transaction_message = 'Напишите ваше сообщение'


def get_transaction_message(transaction: Transaction, message):
    description = f'{transaction.have_amount} {transaction.have_currency} {"➡️" if message.from_merchant else "⬅️"}' \
                  f' {transaction.get_amount} {transaction.get_currency}'

    return {
        'text': f'✉️ Новое сообщение'
                f'\nЗаявка #{transaction.id}'
                f'\n{description}'
                f'\n\n{message.text}',
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('📩 Ответить', callback_data=transaction_messages.new(
                id = transaction.id, action = TransAction.write_message)),
            InlineKeyboardButton('ℹ Заявка', callback_data=transaction_messages.new(
                id = transaction.id, action = TransAction.main)),
        )
    }


def get_transaction_message_history(transaction: Transaction):
    history_text = ''
    for mes in transaction.messages:
        if mes.from_merchant:
            history_text += f'\nMerchant: {fmt.italic(mes.text)}'
        else:
            history_text += f'\nMaker: {fmt.italic(mes.text)}'

    return {
        'text': f'✉️ История сообщений'
                f'\nЗаявка #{transaction.id}'
                f'\n{history_text}',
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('ℹ Заявка', callback_data = transaction_messages.new(
                id = transaction.id, action = TransAction.main)),
        )
    }
