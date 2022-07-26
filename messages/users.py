from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from database.models.transaction import fiat_currency, all_currency, Currency

from config import USER_COMMISSION, AUTH_USER_COMMISSION, MERCHANT_COMMISSION

start_screen_allow = {
    'text': 'Привет.\n\n Для аутентификации вам нужно указать номер телефона. Так мы будем понимать серьезность ваших заявок.',
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True).row(
        KeyboardButton(text = 'Готов к обмену', request_contact = True)
    )
}

start_screen_username_not = {
    'text': 'Привет.\n\n Ваш username не указан. Мы не можем аутентифицировать вас.'
}

main_screen = {
    'text': 'Главное меню'
            '\n'
            '\nТранкзакции:'
            '\n/newtrans - Создать новую транкзакцию'
            '\n/mytrans - Показать мои транкзакции'
            '\n'
            '\nКурсы:'
            '\n/rates'
}

make_transaction_have_currency = {
    'text': 'Какую валюту вы хотите обменять?',
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True).add(
        *[KeyboardButton(i) for i in all_currency]
    )
}

make_transaction_get_fiat_currency = {
    'text': 'Какую валюту вы бы хотели получить?',
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True).add(
        *[KeyboardButton(i) for i in fiat_currency]
    )
}


def make_transaction_amount(currency):
    return {
        'text': f'Напишите количество {currency} валюты, которую вы хотите обменять'
    }


def make_transaction_rate(have_currency, get_currency):
    return {
        'text': f'Напишите желаемый курс для обмена {have_currency} ➡️ {get_currency}'
    }


make_transaction_incorrect_number = {
    'text': 'Вы ввели неверное значение.\n\n Допустимые значения: 12, 10.1, 10.11. Так же нельзя указывать десятичное '
            'значение, больше сотых.'
}


make_transaction_cd = CallbackData('trans', 'have_currency', 'get_currency', 'amount', 'rate')


def make_transaction_show(have_currency, get_currency, amount: float | int, rate: float | int, auth_user=False):
    if have_currency == Currency.RUB and get_currency == Currency.BAT:
        get_amount = round(amount / rate, 2)
    elif have_currency == Currency.BAT and get_currency == Currency.RUB:
        get_amount = round(amount * rate, 2)
    elif have_currency == Currency.USDT and get_currency == Currency.BAT:
        get_amount = round(amount * rate, 2)
    elif have_currency == Currency.BAT and get_currency == Currency.USDT:
        get_amount = round(amount / rate, 2)
    else:
        raise f"pair {have_currency} -> {get_currency} not allowed"

    commission = round(get_amount * (AUTH_USER_COMMISSION if auth_user else USER_COMMISSION / 100), 2)
    get_amount_without_commission = round(get_amount - commission, 2)
    return {
        'text': f'🤝 Отдаёте: {amount} {have_currency}'
                f'\n🤝 Получаете: {get_amount_without_commission} {get_currency}'
                f'\n💸 Комиссия: {commission} {get_currency}'
                f'\n📉 Курс: {rate}',
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('✅ Опубликовать', callback_data = make_transaction_cd.new(have_currency, get_currency,
                                                                                           amount, rate)),
            InlineKeyboardButton('❌ Отменить', callback_data = 'del_message'))
    }
