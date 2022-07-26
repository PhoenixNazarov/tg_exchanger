from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from sqlalchemy import or_
from database.models import Transaction, User
from database.models.transaction import TransStatus
from database.models.transaction import get_russian_status
from share import session_factory


def get_screen_transaction_user(transaction: Transaction):
    if transaction.status == TransStatus.in_stack:
        return {
            'text': get_transaction_user(transaction),
            'reply_markup': get_transaction_keyboard_cancel(transaction)
        }
    elif transaction.status == TransStatus.canceled:
        return {
            'text': get_transaction_user(transaction),
            'reply_markup': InlineKeyboardMarkup()
        }


def get_transaction_user(transaction: Transaction):
    text = f'Заявка #{transaction.id}' \
           f'\n🤝 Отдаёте: {transaction.have_amount} {transaction.have_currency}' \
           f'\n🤝 Получаете: {transaction.get_amount} {transaction.get_currency}' \
           f'\n💸 Комиссия: {transaction.commission_user} {transaction.get_currency}' \
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


def get_transaction_merchant(transaction: Transaction):
    with session_factory() as session:
        user = session.query(User).get(transaction.user_id)

    return f'Заявка #{transaction.id}' \
           f'\n🤝 Получаете: {transaction.have_amount} {transaction.have_currency}' \
           f'\n🤝 Отдаёте: {transaction.get_amount} {transaction.get_currency}' \
           f'\n💸 Комиссия пользователя: {transaction.commission_user} {transaction.get_currency}' \
           f'\n💸 Комиссия мерчанта: {transaction.commission_merchant} {transaction.have_currency}' \
           f'\n📉 Курс: {transaction.rate}'
    # f'\n' \
    # f'\n👔 Пользователь: @{user.username}' \
    # f'\n📱: {user.phone}' \
    # f'\n🏁: {user.good_transactions}'


accept_trans_merchant = CallbackData('mtrans', 'id', 'accept', 'ban')


def get_transaction_keyboard(transaction: Transaction):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton('✅ Принять',
                             callback_data = accept_trans_merchant.new(id = transaction.id, accept = 1, ban = 0)),
        InlineKeyboardButton('❌ Пожаловаться',
                             callback_data = accept_trans_merchant.new(id = transaction.id, accept = 0, ban = 1))

    )


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
