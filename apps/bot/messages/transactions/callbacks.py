from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from strenum import StrEnum

from database.models import Transaction
from database.models.transaction import TransStatus
from . import _
from apps.bot.messages.options import RepeatingText


class TransAction(StrEnum):
    main = 'main'
    write_message = 'write_message'
    show_messages = 'show_messages'
    accept = 'accept'
    cancel = 'cancel'


# MERCHANT_CHANNEL
accept_trans_merchant = CallbackData('mtrans', 'id', 'accept', 'ban')

# MAKER
edit_trans_user_p = CallbackData('edittrans_p', 'id')
edit_trans_user = CallbackData('edittrans', 'id', 'have_amount', 'rate', 'get_amount')
make_transaction_cd = CallbackData('trans', 'id', 'public')

cancel_trans_user_m = CallbackData('canceltrans', 'id')
cancel_trans_user_a = CallbackData('canceltransa', 'id', 'yes', 'no')

transaction_messages = CallbackData('trans_in_exc', 'id', 'action')
transaction_messages_cancel_proof = CallbackData('trans_cancel_p', 'id', 'proof')
transaction_messages_accept_proof = CallbackData('trans_accept_p', 'id', 'proof')


def get_transaction_keyboard_cancel(transaction: Transaction):
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(RepeatingText.edit, callback_data = edit_trans_user_p.new(id = transaction.id))
    ).row(
        InlineKeyboardButton(RepeatingText.cancel, callback_data = cancel_trans_user_m.new(id = transaction.id)))


def transaction_cancel_a(text, trans_id):
    return {
        'text': _('Are you sure you want to delete this application?:'
                  '\n{transaction_text}').format(transaction_text = text),
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton(RepeatingText.yes, callback_data = cancel_trans_user_a.new(id = trans_id, yes = 1, no = 0)),
            InlineKeyboardButton(RepeatingText.no, callback_data = cancel_trans_user_a.new(id = trans_id, yes = 0, no = 1))
        )}


def get_transaction_keyboard_main(transaction: Transaction, merchant=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(_('📩 Write a message'),
                             callback_data = transaction_messages.new(id = transaction.id,
                                                                      action = TransAction.write_message)),
        InlineKeyboardButton(_('✉️ Message history'),
                             callback_data = transaction_messages.new(id = transaction.id,
                                                                      action = TransAction.show_messages)))

    if not merchant and transaction.status == TransStatus.in_exchange:
        keyboard.row(InlineKeyboardButton(RepeatingText.edit, callback_data = edit_trans_user_p.new(id = transaction.id)))

    if (merchant and transaction.status == TransStatus.in_exchange) or (
            not merchant and transaction.status == TransStatus.wait_good_user):
        keyboard.row(
            InlineKeyboardButton(_(RepeatingText.accept),
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.accept)),
            InlineKeyboardButton(RepeatingText.complain,
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.cancel)))
    else:
        keyboard.row(
            InlineKeyboardButton(RepeatingText.complain,
                                 callback_data = transaction_messages.new(id = transaction.id,
                                                                          action = TransAction.cancel)))
    return keyboard


def get_transaction_keyboard_accept(transaction: Transaction, merchant=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(RepeatingText.accept,
                             callback_data = transaction_messages_accept_proof.new(id = transaction.id, proof = 1)),
        InlineKeyboardButton(RepeatingText.transaction,
                             callback_data = transaction_messages.new(id = transaction.id, action = TransAction.main)))
    return keyboard
