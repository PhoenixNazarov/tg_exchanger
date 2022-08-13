from database.models import Merchant
from . import _


def help_admin():
    return {
        'text': _('/admin_help'
                  '\n'
                  '\n/add_merch <id>'
                  '\n/del_merch <id>'
                  '\n/list_merch'
                  '\n/set_limit_amount <id> <value>'
                  '\n/set_accumulated_commission <id> [currency usd, thb, rub] [value] - default set 0 in all currency')
    }


def admin_wrong_count_arguments():
    return {
        'text': _('You write wrong count arguments for this command')
    }


def admin_wrong_id():
    return {
        'text': _('Id should be number')
    }


def admin_wrong_count():
    return {
        'text': _('Value should be number')
    }


def admin_wrong_currency():
    return {
        'text': _('Value should be currency')
    }


def admin_id_not_found():
    return {
        'text': _('User with that id dont write the bot')
    }


def admin_merchant_add(merchant: Merchant):
    return {
        'text': _('Add merchant: {merchant.id}').format(merchant = merchant)
    }


def admin_merchant_del(merchant_id):
    return {
        'text': _('Delete merchant: {merchant_id}').format(merchant_id = merchant_id)
    }


def admin_merchant_list(merchant: Merchant):
    return {
        'text': _('Merchant:'
                  '\n{merchant.id}'
                  '\n{merchant.user.username}'
                  '\nAllow amount: {merchant.allow_max_amount}'
                  '\nAccumulated commission:'
                  '\nUsd: {merchant.accumulated_commission.usd}'
                  '\nThb: {merchant.accumulated_commission.thb}'
                  '\nRub: {merchant.accumulated_commission.rub}').format(merchant = merchant)
    }
