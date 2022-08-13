from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from . import _

start_screen_allow = {
    'text': _(
        'Hi.\n\nYou need to provide a phone number for authentication. So we will understand the seriousness of your '
        'applications'),
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).row(
        KeyboardButton(text = _('Ready to trade'), request_contact = True)
    )
}

start_screen_username_not = {
    'text': _('Hi.\n\nYour username is not specified. We cannot authenticate you.\nAdd username and write /start')
}

main_screen = {
    'text': _('Main menu'
              '\n'
              '\nTransactions:'
              '\n/newtrans - Create new transaction'
              '\n/mytrans - Show my transactions'
              '\n'
              '\nRates:'
              '\n/rates')
}
