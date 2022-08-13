from . import _
from .options import *


def get_transaction_merchant(transaction):
    if transaction.status == TransStatus.in_exchange:
        return {
            'text': get_transaction_merchant_default(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction, True)
        }
    elif transaction.status == TransStatus.wait_good_user:
        return {
            'text': get_transaction_merchant_default(transaction),
            'reply_markup': get_transaction_keyboard_main(transaction, True)
        }
    elif transaction.status == TransStatus.good_finished:
        return {
            'text': get_transaction_merchant_default(transaction),
        }


def get_transaction_merchant_default(transaction: Transaction):
    return _('Transaction #{transaction.id}'
             '\n{transaction_merchant_description}'
             '\n{transaction_receive_description}').format(
        transaction = transaction,
        transaction_merchant_description = get_trans_description_merchant(transaction),
        transaction_receive_description= get_transaction_type_thb_detail(transaction)
    )