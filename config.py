from data.local import *

USD_THB = 33

SQL_PATH = 'sqlite:///data/database.db'
LOCALES_PATH = 'data/locales'

USER_COMMISSION = 0
AUTH_USER_COMMISSION = 0
MERCHANT_COMMISSION = 0.1

MAIN_COMMANDS = ['/newtrans', '/mytrans']

TOWNS = {
    "Phuket": ["Rawai", "Chalong", "Karta", "Karon", "Patong", "Kamala", "Surin", "Bangtao", "Laguna", "Katu"],
    "Phangan": ["Haad Yao", "Haad Salad"],
    "Koh Samui": ["Chawang", "Beach"]
}

BANKS = ["Krungsri", "Bangkok Bank", "Kasikorn Bank"]
