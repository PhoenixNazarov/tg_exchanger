from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.models.transaction_moderate import *
from . import _
import config
from .options import *

make_transaction_have_currency = {
    'text': _('What currency do you want to exchange?'),
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(
        *[KeyboardButton(i) for i in all_currency]
    )
}

make_transaction_get_fiat_currency = {
    'text': _('What currency would you like to receive?'),
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(
        *[KeyboardButton(i) for i in fiat_currency]
    )
}


def make_transaction_amount(currency):
    return {
        'text': _('Write the amount of {currency} of the currency you want to exchange').format(currency = currency),
        'reply_markup': ReplyKeyboardRemove()
    }


def make_transaction_rate(have_currency, get_currency):
    return {
        'text': _('Write the desired exchange rate {have_currency} ➡️ {get_currency}').format(
            have_currency = have_currency,
            get_currency = get_currency)
    }


make_transaction_incorrect_number = {
    'text': _(
        "You entered an invalid value.\n\n Valid values: 12, 10.1, 10.11. You also can't use decimal "
        'value, greater than hundredths.')
}


def make_transaction_get_type_thb():
    return {
        'text': _("Select the type of receipt THB"),
        'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(
            KeyboardButton(transaction_get[TransGet.cash]),
            KeyboardButton(transaction_get[TransGet.bank_balance])
        ).add(
            KeyboardButton(transaction_get[TransGet.atm_machine])
        )
    }


def make_transaction_town():
    return {
        'text': _('Choose city'),
        'reply_markup':
            ReplyKeyboardMarkup(resize_keyboard = True).add(*[KeyboardButton(i) for i in config.TOWNS.keys()])
    }


def make_transaction_region(town):
    return {
        'text': _('Choose an area'),
        'reply_markup':
            ReplyKeyboardMarkup(resize_keyboard = True).add(*[KeyboardButton(i) for i in config.TOWNS[town]])
    }


def make_transaction_bank():
    return {
        'text': _('Select receiving bank'),
        'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(*[KeyboardButton(i) for i in config.BANKS])
    }


def make_transaction_number():
    # todo load prev
    return {
        'text': _('Write the receipt invoice in the format: 9570147158'),
        'reply_markup': ReplyKeyboardRemove()
    }


def make_transaction_name():
    return {
        'text': _('Write the Initials attached to the card in the format: Denis Mandrikov'),
        'reply_markup': ReplyKeyboardRemove()
    }


def make_transaction_end():
    return {
        'text': _('Application creation completed'),
        'reply_markup': ReplyKeyboardRemove()
    }


def make_transaction_show(transaction: TransactionModerate):
    return {
        'text': _('{transaction_user_description}'
                  '\n{transaction_receive_description}').format(
            transaction_user_description = get_trans_description_user(transaction),
            transaction_receive_description = get_transaction_type_thb_detail(transaction, True),
            transaction = transaction),
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton(RepeatingText.publish,
                                 callback_data = make_transaction_cd.new(id = transaction.id, public = 1)),
            InlineKeyboardButton(RepeatingText.cancel,
                                 callback_data = make_transaction_cd.new(id = transaction.id, public = 0)))
    }
