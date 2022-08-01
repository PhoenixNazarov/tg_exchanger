from database.models.transaction import *
from share import dp, bot, session_maker


def calculate_transaction_get_amount(transaction: Transaction, auth_user) -> None:
    if transaction.have_currency in not_stable_currency and transaction.get_currency == Currency.BAT:
        get_amount = round(transaction.have_amount / transaction.rate, 2)
    elif transaction.have_currency == Currency.BAT and transaction.get_currency in not_stable_currency:
        get_amount = round(transaction.have_amount * transaction.rate, 2)
    elif transaction.get_currency == Currency.BAT:
        get_amount = round(transaction.have_amount * transaction.rate, 2)
    elif transaction.have_currency == Currency.BAT:
        get_amount = round(transaction.have_amount / transaction.rate, 2)
    else:
        raise f"pair {transaction.have_currency} -> {transaction.get_currency} not allowed"

    commission = round(get_amount * (AUTH_USER_COMMISSION if auth_user else USER_COMMISSION / 100), 2)
    get_amount_without_commission = round(get_amount - commission, 2)

    transaction.get_amount = get_amount_without_commission
    transaction.commission_user = commission
    transaction.commission_merchant = round(transaction.have_amount * (MERCHANT_COMMISSION / 100), 2)


def calculate_transaction_have_amount(transaction: Transaction, auth_user) -> None:
    if transaction.have_currency in not_stable_currency and transaction.get_currency == Currency.BAT:
        have_amount = round(transaction.get_amount * transaction.rate, 2)
    elif transaction.have_currency == Currency.BAT and transaction.get_currency in not_stable_currency:
        have_amount = round(transaction.get_amount / transaction.rate, 2)
    elif transaction.get_currency == Currency.BAT:
        have_amount = round(transaction.get_amount / transaction.rate, 2)
    elif transaction.have_currency == Currency.BAT:
        have_amount = round(transaction.get_amount * transaction.rate, 2)
    else:
        raise f"pair {transaction.have_currency} -> {transaction.get_currency} not allowed"

    commission = round(transaction.get_amount * (AUTH_USER_COMMISSION if auth_user else USER_COMMISSION / 100), 2)
    get_amount_without_commission = round(transaction.get_amount - commission, 2)

    transaction.get_amount = get_amount_without_commission
    transaction.commission_user = commission
    transaction.commission_merchant = round(transaction.have_amount * (MERCHANT_COMMISSION / 100), 2)
    transaction.have_amount = have_amount
