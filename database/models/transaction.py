import enum

from sqlalchemy import Column, Float, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from strenum import StrEnum

from config import *
from .base import BaseModelWithId
from .transaction_message import MessageTransaction
from .transaction_requisits import RequisitesCash, RequisitesBankBalance


class Currency(StrEnum):
    BAT = 'BAT'
    RUB = 'RUB'
    USDT = 'USDT'
    USDC = 'USDC'


not_stable_currency = [Currency.RUB]

all_currency = [str(Currency.USDT), str(Currency.USDC), str(Currency.RUB), str(Currency.BAT)]
fiat_currency = [str(Currency.USDT), str(Currency.USDC), str(Currency.RUB)]


class TransStatus(enum.Enum):
    in_stack = 0
    in_exchange = 1
    wait_good_user = 2
    canceled = -1
    good_finished = -2

    bad_finished_by_user = -6
    bad_finished_by_merchant = -7


class TransGet(StrEnum):
    none = 'none'
    cash = 'cash'
    atm_machine = 'atm_machine'
    bank_balance = 'bank_balance'


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

    get_thb_type = Column(Enum(TransGet), nullable = False)
    req_cash = relationship(RequisitesCash, backref = 'transactions', uselist = False)
    req_bank = relationship(RequisitesBankBalance, backref = 'transactions', uselist = False)

    messages = relationship(MessageTransaction, backref = 'transactions')
