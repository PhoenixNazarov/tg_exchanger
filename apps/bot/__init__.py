from aiogram import Dispatcher, executor
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from share import bot
from .filters import bind_filters
from .middleware import i18n
from .handlers import register_handlers
import config


def start_bot():
    storage = RedisStorage2('localhost', config.REDIS_PORT, password = 'redispw')
    dp = Dispatcher(bot, storage = storage)

    dp.middleware.setup(i18n)
    bind_filters(dp)
    register_handlers(dp)
    executor.start_polling(dp, skip_updates = True)
