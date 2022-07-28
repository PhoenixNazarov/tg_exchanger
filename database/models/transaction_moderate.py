import enum

from sqlalchemy import Column, Float, ForeignKey, Enum, Integer, Text
from sqlalchemy.orm import relationship

from config import *
from .base import BaseModelWithId
from .transaction import *


class TransactionModerate(BaseModelWithId):
    __tablename__ = 'transactions_moderate'

    user_id = Column(ForeignKey('users.id'), nullable = False)

    have_amount = Column(Float, nullable = False)
    have_currency = Column(Enum(Currency), nullable = False)
    get_amount = Column(Float, nullable = False)
    get_currency = Column(Enum(Currency), nullable = False)
    rate = Column(Float, nullable = False)

    commission_user = Column(Float, nullable = False)
    commission_merchant = Column(Float, nullable = False)

    get_thb_type = Column(Enum(TransGet), nullable = False)

    option1 = Column(Text)
    option2 = Column(Text)
    option3 = Column(Text)

    def __init__(self, amount, have_currency, get_currency, rate, auth_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.have_amount = amount
        self.have_currency = have_currency
        self.get_currency = get_currency
        self.rate = rate

        if have_currency in not_stable_currency and get_currency == Currency.BAT:
            get_amount = round(amount / rate, 2)
        elif have_currency == Currency.BAT and get_currency in not_stable_currency:
            get_amount = round(amount * rate, 2)
        elif get_currency == Currency.BAT:
            get_amount = round(amount * rate, 2)
        elif have_currency == Currency.BAT:
            get_amount = round(amount / rate, 2)
        else:
            raise f"pair {have_currency} -> {get_currency} not allowed"

        commission = round(get_amount * (AUTH_USER_COMMISSION if auth_user else USER_COMMISSION / 100), 2)
        get_amount_without_commission = round(get_amount - commission, 2)

        self.get_amount = get_amount_without_commission
        self.commission_user = commission
        self.commission_merchant = round(self.have_amount * (MERCHANT_COMMISSION / 100), 2)
