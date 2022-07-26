from aiogram import executor
from share import dp

import handlers


executor.start_polling(dp, skip_updates=True)
