from sqlalchemy import or_

from . import _
from share import session_factory
from .options import *


def get_transaction_user(transaction: Transaction):
    if transaction.status == TransStatus.in_stack:
        return {
            'text': get_transaction_user_default(transaction),
            'reply_markup': get_transaction_keyboard_cancel(transaction)
        }
    elif transaction.status == TransStatus.in_exchange:
        return {
            'text': get_transaction_user_default(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction)
        }
    elif transaction.status == TransStatus.wait_good_user:
        return {
            'text': get_transaction_user_default(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction)
        }
    elif transaction.status == TransStatus.good_finished:
        return {
            'text': get_transaction_user_default(transaction),
        }
    elif transaction.status == TransStatus.canceled:
        return {
            'text': get_transaction_user_default(transaction)
        }


def get_transaction_user_place_line(transaction):
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
    return _("\n🥉 Place in line: {position}").format(position = position)


def get_transaction_user_default(transaction: Transaction):
    text = _('Transaction #{transaction.id}'
             '\n{transaction_user_description}'
             '\n👔 Status: {status}'
             '{transaction_receive_description}').format(
        transaction = transaction,
        transaction_user_description = get_trans_description_user(transaction),
        status = transaction_status[transaction.status],
        transaction_receive_description = get_transaction_type_thb_detail(transaction)
    )

    if transaction.status == TransStatus.in_stack:
        text += get_transaction_user_place_line(transaction)

    return text


def get_transaction_keyboard_change(transaction: Transaction):
    return {
        'text': _('What do you want to change?'
                  '\n{transaction_user_default}').format(
            transaction_user_default = get_transaction_user_default(transaction),
            transaction = transaction
        ),
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton(_('⚙️ Amount of given currency'),
                                 callback_data = edit_trans_user.new(id = transaction.id, have_amount = 1, rate = 0,
                                                                     get_amount = 0))
        ).row(
            InlineKeyboardButton(_('⚙️ Rate'),
                                 callback_data = edit_trans_user.new(id = transaction.id, have_amount = 0, rate = 1,
                                                                     get_amount = 0))
        ).row(
            InlineKeyboardButton(_('⚙️ Amount of received currency'),
                                 callback_data = edit_trans_user.new(id = transaction.id, have_amount = 0, rate = 0,
                                                                     get_amount = 1))
        ).row(
            InlineKeyboardButton(RepeatingText.transaction,
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.main))
        )}
