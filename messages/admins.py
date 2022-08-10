from database.models import Merchant


def help_admin():
    return {
        'text': '/admin_help'
                '\n'
                '\n/add_merch <id>'
                '\n/del_merch <id>'
                '\n/list_merch'
                '\n/set_limit_merch'
                '\n\n/accumulated_commission <id>'
                '\n/set_commission <id> <count>'
    }


def admin_wrong_count_arguments():
    return {
        'text': 'You write wrong count arguments for this command'
    }


def admin_wrong_id():
    return {
        'text': 'Id should be number'
    }


def admin_id_not_found():
    return {
        'text': 'User with that id dont write the bot'
    }


def admin_merchant_add(merchant: Merchant):
    return {
        'text': 'Add merchant: {merchant.id}'.format(merchant = merchant)
    }


def admin_merchant_del(merchant_id):
    return {
        'text': 'Delete merchant: {merchant_id}'.format(merchant_id = merchant_id)
    }


def admin_merchant_list(merchant: Merchant):
    return {
        'text': 'Merchant'
                '\n{merchant.id}'
                '\n{merchant.user.username}'.format(merchant = merchant)
    }