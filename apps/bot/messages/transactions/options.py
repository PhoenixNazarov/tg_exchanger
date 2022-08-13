from . import _
from database.models.transaction import TransGet
from .callbacks import *


transaction_get = {
    TransGet.cash: _('Cash'),
    TransGet.atm_machine: _('Cash by code'),
    TransGet.bank_balance: _('Transfer')
}

transaction_status = {
    TransStatus.in_stack: _('Waiting for a merchant'),
    TransStatus.in_exchange: _('In work'),
    TransStatus.wait_good_user: _('Waiting for a user'),
    TransStatus.good_finished: _('Finished'),
    TransStatus.canceled: _('Canceled')
}


def get_transaction_type_thb_detail(transaction: Transaction, trans_moderate=False):
    if transaction.get_thb_type == TransGet.cash:
        town = transaction.req_cash.town
        region = transaction.req_cash.region
        if trans_moderate:
            town = transaction.option1
            region = transaction.option2

        return _('💳 Receipt type: {transaction_get}'
                 '\n🏙: {town}, {region}').format(
            transaction_get = transaction_get[TransGet.cash], town = town, region = region)
    elif transaction.get_thb_type == TransGet.atm_machine:
        return _('💳 Receipt type: {transaction_get}').format(
            transaction_get = transaction_get[TransGet.cash])
    elif transaction.get_thb_type == TransGet.bank_balance:
        bank_name = transaction.req_bank.bank_name
        number = transaction.req_bank.number
        name = transaction.req_bank.name
        if trans_moderate:
            bank_name = transaction.option1
            number = transaction.option2
            name = transaction.option3

        return _('💳 Receipt type: {transaction_get}'
                 '\n🏦: {bank_name} {number}'
                 '\n👨‍💼: {name}').format(
            transaction_get = transaction_get[TransGet.cash], bank_name = bank_name, number = number, name = name,
            transaction = transaction)
    return ''


def get_transaction_type_thb_short(transaction: Transaction):
    if transaction.get_thb_type == TransGet.cash:
        return _('💳 Receipt type: {transaction_get}'
                 '\n🏙: {transaction.req_cash.town}, {transaction.req_cash.region}').format(
            transaction_get = transaction_get[TransGet.cash], transaction = transaction)
    elif transaction.get_thb_type == TransGet.atm_machine:
        return _('💳 Receipt type: {transaction_get}').format(
            transaction_get = transaction_get[TransGet.cash])
    elif transaction.get_thb_type == TransGet.bank_balance:
        return _('💳 Receipt type: {transaction_get}'
                 '\n🏦: {transaction.req_bank.bank_name}').format(
            transaction_get = transaction_get[TransGet.cash], transaction = transaction)
    return ''


def get_trans_description_universal(transaction: Transaction, merchant):
    return f'{transaction.have_amount} {transaction.have_currency} {"➡️" if merchant else "⬅️"}' \
                  f' {transaction.get_amount} {transaction.get_currency}'


def get_trans_description_channel(transaction: Transaction):
    return _('🤝 Get: {transaction.have_amount} {transaction.have_currency}'
             '\n🤝 Give: {transaction.get_amount} {transaction.get_currency}'
             '\n💸 Merchant commission: {transaction.commission_merchant} {transaction.have_currency}'
             '\n📉 Rate: {transaction.rate}').format(transaction = transaction)


def get_trans_description_merchant(transaction: Transaction):
    return _('🤝 Get: {transaction.have_amount} {transaction.have_currency}'
             '\n🤝 Give: {transaction.get_amount} {transaction.get_currency}'
             '\n💸 Merchant commission: {transaction.commission_merchant} {transaction.have_currency}'
             '\n📉 Rate: {transaction.rate}'
             '\n👔 Status: {transaction_status[transaction.status]} ').format(transaction = transaction)


def get_trans_description_user(transaction: Transaction):
    return _('🤝 Give: {transaction.get_amount} {transaction.get_currency}'
             '\n🤝 Get: {transaction.have_amount} {transaction.have_currency}'
             '\n📉 Rate: {transaction.rate}').format(transaction = transaction)
