from aiogram.contrib.middlewares.i18n import I18nMiddleware
import config

I18N_DOMAIN = 'exchanger'
LOCALES_DIR = config.LOCALES_PATH

i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
_ = i18n.gettext
