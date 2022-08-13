from .admins import register_handlers_admin
from .channel import register_handlers_channel
from .users import register_handlers_user


def register_handlers(dp):
    register_handlers_admin(dp)
    register_handlers_channel(dp)
    register_handlers_user(dp)
