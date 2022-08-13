import aiogram.utils.markdown as fmt
from . import _
from .merchant import *
from .user import *


def accept_status(transaction: Transaction, merchant):
    return {
        'text':
            _('Did you receive money?'
              '\n{transaction_description}').format(
                transaction_description = get_transaction_merchant_default(
                    transaction) if merchant else get_transaction_user_default(
                    transaction)),
        'reply_markup': get_transaction_keyboard_accept(transaction)
    }


def cant_write():
    return {
        'text': _("Can't write a message, transaction completed")
    }


cant_accept = _("'You can't change the status for this ticket'")


def get_accept_status(transaction, merchant):
    screen = get_transaction_merchant(transaction) if merchant else get_transaction_user(transaction)
    screen['text'] = _('Application status changed') + '\n' + screen['text']
    return screen


def get_transaction_merchant_edit(transaction):
    screen = get_transaction_merchant(transaction)
    screen['text'] = _('User updated ticket') + '\n' + screen['text']
    return screen


cant_cancel_transaction = {
    'text': _('You cannot cancel this transaction')
}

# MESSAGES
havenot_messages = _('No messages found')
write_transaction_message = _('Write your message')


def get_transaction_message(transaction: Transaction, message):
    return {
        'text': _('✉️ A new message'
                  '\nTransaction #{transaction.id}'
                  '\n{transaction_inline_description}'
                  '\n\n{message.text}').format(
            transaction = transaction,
            transaction_inline_description = get_trans_description_universal(transaction, message.from_merchant),
            message = message
        ),
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('📩 Answer', callback_data = transaction_messages.new(
                id = transaction.id, action = TransAction.write_message)),
            InlineKeyboardButton(RepeatingText.transaction, callback_data = transaction_messages.new(
                id = transaction.id, action = TransAction.main)),
        )
    }


def get_transaction_message_history(transaction: Transaction):
    history_text = ''
    for mes in transaction.messages:
        if mes.from_merchant:
            history_text += _('\nMerchant: {message}').foramat(message = fmt.italic(mes.text))
        else:
            history_text += _('\nMaker: {message}').format(message = fmt.italic(mes.text))

    return {
        'text': _('✉️ Message history'
                  '\nTransaction #{transaction.id}'
                  '\n{history_text}').format(transaction = transaction, history_text = history_text),
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton(RepeatingText.transaction, callback_data = transaction_messages.new(
                id = transaction.id, action = TransAction.main)),
        )
    }


# EDIT
transaction_edit_write_have_amount = {
    'text': _('Write the amount you want to exchange')
}

transaction_edit_write_rate = {
    'text': _('Write a new course')
}

transaction_edit_write_get_amount = {
    'text': _('Write the quantity you want to receive')
}

havenot_transactions = {
    'text': _("You don't have any active tickets."
              "\nTo create an order type /newtrans")
}
