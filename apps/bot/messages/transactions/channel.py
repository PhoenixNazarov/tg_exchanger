from share import session_factory
from . import _
from database.models import User
from .options import *


def not_allow_transaction():
    return {
        'text': _('You cant accept this transaction')
    }


def get_transaction_channel(transaction: Transaction):
    if transaction.status == TransStatus.in_stack:
        return get_transaction_channel_in_stack(transaction)
    elif transaction.status == TransStatus.in_exchange:
        return get_transaction_channel_in_exchange(transaction)
    else:
        return get_transaction_channel_in_exchange(transaction)


def get_transaction_channel_in_stack(transaction: Transaction):
    with session_factory() as session:
        user = session.query(User).get(transaction.user_id)

    return {
        'text':
            _('Transaction #{transaction.id}'
              '\n{transaction_channel_description}'
              '\n{transaction_receive_description}').format(transaction = transaction,
                                                            transaction_channel_description = get_trans_description_channel(
                                                                transaction),
                                                            transaction_receive_description = get_transaction_type_thb_short(
                                                                transaction)),
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton(RepeatingText.accept,
                                 callback_data = accept_trans_merchant.new(id = transaction.id, accept = 1,
                                                                           ban = 0)),
            InlineKeyboardButton(RepeatingText.complain,
                                 callback_data = accept_trans_merchant.new(id = transaction.id, accept = 0,
                                                                           ban = 1)))

    }


def get_transaction_channel_in_exchange(transaction: Transaction):
    with session_factory() as session:
        user = session.query(User).get(transaction.merchant_id)
        return {
            'text':
                _('Transaction #{transaction.id}'
                  '\n{transaction_channel_description}'
                  '\n{transaction_receive_description}'
                  '\n👨‍💼 Merchant: @{user.username}').format(
                    transaction = transaction,
                    transaction_channel_description = get_trans_description_channel(transaction),
                    transaction_receive_description = get_transaction_type_thb_short(
                        transaction), user = user),
        }
