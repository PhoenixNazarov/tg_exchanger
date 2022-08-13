from .accept_transaction import register_handlers_accept_transaction


def register_handlers_channel(dp):
    register_handlers_accept_transaction(dp)
