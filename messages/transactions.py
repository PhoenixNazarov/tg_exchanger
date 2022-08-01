import aiogram.utils.markdown as fmt
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from sqlalchemy import or_
from strenum import StrEnum

from database.models import Transaction, User
from database.models.transaction import TransStatus, TransGet
from database.models.transaction import get_russian_status
from messages.users import transaction_get
from share import session_factory


# GET THB
def get_transaction_type_thb_detail(transaction: Transaction):
    if transaction.get_thb_type == TransGet.cash:
        return f'\n💳 Тип получения: {transaction_get[TransGet.cash]}' \
               f'\n🏙: {transaction.req_cash.town}, {transaction.req_cash.region}'
    elif transaction.get_thb_type == TransGet.atm_machine:
        return f'\n💳 Тип получения: {transaction_get[TransGet.atm_machine]}'
    elif transaction.get_thb_type == TransGet.bank_balance:
        return f'\n💳 Тип получения: {transaction_get[TransGet.bank_balance]}' \
               f'\n🏦: {transaction.req_bank.bank_name} {transaction.req_bank.number}' \
               f'\n👨‍💼: {transaction.req_bank.name}'
    return ''


def get_transaction_type_thb_short(transaction: Transaction):
    if transaction.get_thb_type == TransGet.cash:
        return f'\n💳 Тип получения: {transaction_get[TransGet.cash]}' \
               f'\n🏙: {transaction.req_cash.town}, {transaction.req_cash.region}'
    elif transaction.get_thb_type == TransGet.atm_machine:
        return f'\n💳 Тип получения: {transaction_get[TransGet.atm_machine]}'
    elif transaction.get_thb_type == TransGet.bank_balance:
        return f'\n💳 Тип получения: {transaction_get[TransGet.bank_balance]}' \
               f'\n🏦: {transaction.req_bank.bank_name}'
    return ''


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
                f'\n📉 Курс: {transaction.rate}'
                f'{get_transaction_type_thb_short(transaction)}',
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
                    f'{get_transaction_type_thb_short(transaction)}'
                    f'\n👨‍💼 Мерчант: @{user.username}'
            # f'\n' \
            # f'\n👔 Пользователь: @{user.username}' \
            # f'\n📱: {user.phone}' \
            # f'\n🏁: {user.good_transactions}'\
        }


# MERGE
def accept_status(transaction: Transaction, merchant):
    accept_status = 'Вы получили денежные средства?'
    return {
        'text':
            accept_status + '\n' +
            get_transaction_merchant_in_exc(transaction) if merchant else get_transaction_user_in_exchange(
                transaction),
        'reply_markup': get_transaction_keyboard_accept(transaction)
    }


def cant_write():
    return {
        'text': 'Нельзя написать сообщение, заявка окончена'
    }


cant_accept = 'Нельзя изменить статус для этой заявки'


def get_accept_status(transaction, merchant):
    accept_message = 'Статус заявки изменён'
    screen = get_transaction_merchant(transaction) if merchant else get_screen_transaction_user(transaction)
    screen['text'] = accept_message + '\n' + screen['text']
    return screen


def get_transaction_merchant_edit(transaction):
    accept_message = 'Пользователь обновил заявку'
    screen = get_transaction_merchant(transaction)
    screen['text'] = accept_message + '\n' + screen['text']
    return screen


# MERCHANT
def get_transaction_merchant(transaction):
    if transaction.status == TransStatus.in_exchange:
        return {
            'text': get_transaction_merchant_in_exc(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction, True)
        }
    elif transaction.status == TransStatus.wait_good_user:
        return {
            'text': get_transaction_merchant_in_exc(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction, True)
        }
    elif transaction.status == TransStatus.good_finished:
        return {
            'text': get_transaction_merchant_in_exc(transaction),
        }


def get_transaction_merchant_in_exc(transaction: Transaction):
    return f'Заявка #{transaction.id}' \
           f'\n🤝 Получаете: {transaction.have_amount} {transaction.have_currency}' \
           f'\n🤝 Отдаёте: {transaction.get_amount} {transaction.get_currency}' \
           f'\n💸 Комиссия мерчанта: {transaction.commission_merchant} {transaction.have_currency}' \
           f'\n📉 Курс: {transaction.rate}' \
           f'\n👔 Статус: {get_russian_status[transaction.status]}' \
           f'{get_transaction_type_thb_detail(transaction)}'


# f'\n💸 Комиссия пользователя: {transaction.commission_user} {transaction.get_currency}'


# MAKER
edit_trans_user_p = CallbackData('edittrans_p', 'id')
edit_trans_user = CallbackData('edittrans', 'id', 'have_amount', 'rate', 'get_amount')


def get_screen_transaction_user(transaction: Transaction):
    if transaction.status == TransStatus.in_stack:
        return {
            'text': get_transaction_user(transaction),
            'reply_markup': get_transaction_keyboard_cancel(transaction)
        }
    elif transaction.status == TransStatus.in_exchange:
        return {
            'text': get_transaction_user_in_exchange(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction)
        }
    elif transaction.status == TransStatus.wait_good_user:
        return {
            'text': get_transaction_user_in_exchange(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction)
        }
    elif transaction.status == TransStatus.good_finished:
        return {
            'text': get_transaction_merchant_in_exc(transaction),
        }
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
           f'\n👔 Статус: {get_russian_status[transaction.status]}' \
           f'{get_transaction_type_thb_detail(transaction)}'

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
    return f'Заявка #{transaction.id}' \
           f'\n🤝 Отдаёте: {transaction.have_amount} {transaction.have_currency}' \
           f'\n🤝 Получаете: {transaction.get_amount} {transaction.get_currency}' \
           f'\n📉 Курс: {transaction.rate}' \
           f'\n👔 Статус: {get_russian_status[transaction.status]}' \
           f'{get_transaction_type_thb_detail(transaction)}'


def get_transaction_keyboard_change(transaction: Transaction):
    return {
        'text': 'Что вы хотите изменить?\n' + get_transaction_user_in_exchange(transaction),
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('⚙️ Кол-во отдаваемой валюты',
                                 callback_data = edit_trans_user.new(id = transaction.id, have_amount = 1, rate = 0,
                                                                     get_amount = 0))
        ).row(
            InlineKeyboardButton('⚙️ Курс',
                                 callback_data = edit_trans_user.new(id = transaction.id, have_amount = 0, rate = 1,
                                                                     get_amount = 0))
        ).row(
            InlineKeyboardButton('⚙️ Кол-во получаемой валюты',
                                 callback_data = edit_trans_user.new(id = transaction.id, have_amount = 0, rate = 0,
                                                                     get_amount = 1))
        ).row(
            InlineKeyboardButton('ℹ Заявка',
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.main))
        )}


transaction_edit_write_have_amount = {
    'text': 'Напишите ко-во, которое вы хотите обменять'
}

transaction_edit_write_rate = {
    'text': 'Напишите новый курс'
}

transaction_edit_write_get_amount = {
    'text': 'Напишите ко-во, которое вы хотите получить'
}


havenot_transactions = {
    'text': 'У вас нет активных заявок.'
            '\nДля создания заявки напишите /newtrans'
}

cancel_trans_user_m = CallbackData('canceltrans', 'id')


def get_transaction_keyboard_cancel(transaction: Transaction):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton('⚙️ Изменить', callback_data = edit_trans_user_p.new(id = transaction.id))
    ).row(
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

    if not merchant and transaction.status == TransStatus.in_exchange:
        keyboard.row(InlineKeyboardButton('⚙️ Изменить', callback_data = edit_trans_user_p.new(id = transaction.id)))

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


def get_transaction_keyboard_accept(transaction: Transaction, merchant=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('✅ Подтвердить',
                             callback_data = transaction_messages_accept_proof.new(id = transaction.id, proof = 1)),
        InlineKeyboardButton('ℹ Заявка',
                             callback_data = transaction_messages.new(id = transaction.id, action = TransAction.main)))
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
            InlineKeyboardButton('📩 Ответить', callback_data = transaction_messages.new(
                id = transaction.id, action = TransAction.write_message)),
            InlineKeyboardButton('ℹ Заявка', callback_data = transaction_messages.new(
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
