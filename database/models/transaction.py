import enum

from sqlalchemy import Column, Float, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from strenum import StrEnum

from config import *
from .base import BaseModelWithId


from .transaction_message import MessageTransaction


class Currency(StrEnum):
    BAT = 'BAT'
    RUB = 'RUB'
    USDT = 'USDT'


all_currency = [str(Currency.USDT), str(Currency.RUB), str(Currency.BAT)]
fiat_currency = [str(Currency.USDT), str(Currency.RUB)]


class TransStatus(enum.Enum):
    in_stack = 0
    in_exchange = 1
    wait_good_user = 2
    canceled = -1
    good_finished = -2

    bad_finished_by_user = -6
    bad_finished_by_merchant = -7


get_russian_status = {
    TransStatus.in_stack: 'Ожидание мерчанта',
    TransStatus.in_exchange: 'В работе',
    TransStatus.wait_good_user: 'Ожидание подтверждения пользователя',
    TransStatus.good_finished: 'Завершена',
    TransStatus.canceled: 'Отменена'
}


class Transaction(BaseModelWithId):
    __tablename__ = 'transactions'

    user_id = Column(ForeignKey('users.id'), nullable = False)
    merchant_id = Column(ForeignKey('merchants.id'))

    have_amount = Column(Float, nullable = False)
    have_currency = Column(Enum(Currency), nullable = False)
    get_amount = Column(Float, nullable = False)
    get_currency = Column(Enum(Currency), nullable = False)
    rate = Column(Float, nullable = False)

    commission_user = Column(Float, nullable = False)
    commission_merchant = Column(Float, nullable = False)

    status = Column(Enum(TransStatus), default = TransStatus.in_stack)
    merchant_message_id = Column(Integer)

    messages = relationship(MessageTransaction, backref = 'transactions')

    def __init__(self, amount, have_currency, get_currency, rate, auth_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.have_amount = amount
        self.have_currency = have_currency
        self.get_currency = get_currency
        self.rate = rate

        if have_currency == Currency.RUB and get_currency == Currency.BAT:
            get_amount = round(amount / rate, 2)
        elif have_currency == Currency.BAT and get_currency == Currency.RUB:
            get_amount = round(amount * rate, 2)
        elif have_currency == Currency.USDT and get_currency == Currency.BAT:
            get_amount = round(amount * rate, 2)
        elif have_currency == Currency.BAT and get_currency == Currency.USDT:
            get_amount = round(amount / rate, 2)
        else:
            raise f"pair {have_currency} -> {get_currency} not allowed"

        commission = round(get_amount * (AUTH_USER_COMMISSION if auth_user else USER_COMMISSION / 100), 2)
        get_amount_without_commission = round(get_amount - commission, 2)

        self.get_amount = get_amount_without_commission
        self.commission_user = commission
        self.commission_merchant = round(self.have_amount * (MERCHANT_COMMISSION / 100), 2)
