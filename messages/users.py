from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

import config
from database.models.transaction_moderate import *

start_screen_allow = {
    'text': 'Привет.\n\nДля аутентификации вам нужно указать номер телефона. Так мы будем понимать серьезность ваших заявок.',
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).row(
        KeyboardButton(text = 'Готов к обмену', request_contact = True)
    )
}

start_screen_username_not = {
    'text': 'Привет.\n\nВаш username не указан. Мы не можем аутентифицировать вас.\nДобавьте username и напишите /start'
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
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(
        *[KeyboardButton(i) for i in all_currency]
    )
}

make_transaction_get_fiat_currency = {
    'text': 'Какую валюту вы бы хотели получить?',
    'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(
        *[KeyboardButton(i) for i in fiat_currency]
    )
}


def make_transaction_amount(currency):
    return {
        'text': f'Напишите количество {currency} валюты, которую вы хотите обменять',
        'reply_markup': ReplyKeyboardRemove()
    }


def make_transaction_rate(have_currency, get_currency):
    return {
        'text': f'Напишите желаемый курс для обмена {have_currency} ➡️ {get_currency}'
    }


make_transaction_incorrect_number = {
    'text': 'Вы ввели неверное значение.\n\n Допустимые значения: 12, 10.1, 10.11. Так же нельзя указывать десятичное '
            'значение, больше сотых.'
}

transaction_get = {
    TransGet.cash: 'Наличные',
    TransGet.atm_machine: 'Наличные по коду',
    TransGet.bank_balance: 'Перевод'
}


def make_transaction_get_type_thb():
    return {
        'text': "Выберите тип получения THB",
        'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(
            KeyboardButton(transaction_get[TransGet.cash]),
            KeyboardButton(transaction_get[TransGet.bank_balance])
        ).add(
            KeyboardButton(transaction_get[TransGet.atm_machine])
        )
    }


def make_transaction_town():
    return {
        'text': 'Выберите город',
        'reply_markup':
            ReplyKeyboardMarkup(resize_keyboard = True).add(*[KeyboardButton(i) for i in config.TOWNS.keys()])
    }


def make_transaction_region(town):
    return {
        'text': 'Выберите район',
        'reply_markup':
            ReplyKeyboardMarkup(resize_keyboard = True).add(*[KeyboardButton(i) for i in config.TOWNS[town]])
    }


def make_transaction_end():
    return {
        'text': 'Создание заявки завершено',
        'reply_markup': ReplyKeyboardRemove()
    }


def make_transaction_bank():
    return {
        'text': 'Выберите Банк получения',
        'reply_markup': ReplyKeyboardMarkup(resize_keyboard = True).add(*[KeyboardButton(i) for i in config.BANKS])
    }


def make_transaction_number():
    # todo load prev
    return {
        'text': 'Напишите счет получения в формате: 9570147158',
        'reply_markup': ReplyKeyboardRemove()
    }


def make_transaction_name():
    return {
        'text': 'Напишите Инициалы, привязанные к карте в формате: Denis Mandrikov',
        'reply_markup': ReplyKeyboardRemove()
    }


make_transaction_cd = CallbackData('trans', 'id', 'public')


def make_transaction_show(transaction: TransactionModerate):
    if transaction.get_thb_type == TransGet.cash:
        type_get_thb_descr = f'\n💳 Тип получения: {transaction_get[TransGet.cash]}' \
                             f'\n🏙: {transaction.option1}, {transaction.option2}'
    elif transaction.get_thb_type == TransGet.atm_machine:
        type_get_thb_descr = f'\n💳 Тип получения: {transaction_get[TransGet.atm_machine]}'
    elif transaction.get_thb_type == TransGet.bank_balance:
        type_get_thb_descr = f'\n💳 Тип получения: {transaction_get[TransGet.bank_balance]}' \
                             f'\n🏦: {transaction.option1} {transaction.option2}' \
                             f'\n👨‍💼: {transaction.option3}'
    else:
        type_get_thb_descr = ''

    return {
        'text': f'🤝 Отдаёте: {transaction.have_amount} {transaction.have_currency}'
                f'\n🤝 Получаете: {transaction.get_amount} {transaction.get_currency}'
        # f'\n💸 Комиссия: {commission} {get_currency}'
                f'\n📉 Курс: {transaction.rate}'
                f'{type_get_thb_descr}',
        'reply_markup': InlineKeyboardMarkup().row(
            InlineKeyboardButton('✅ Опубликовать',
                                 callback_data = make_transaction_cd.new(id = transaction.id, public = 1)),
            InlineKeyboardButton('❌ Отменить',
                                 callback_data = make_transaction_cd.new(id = transaction.id, public = 0)))
    }
