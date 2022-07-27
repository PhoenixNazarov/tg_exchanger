from sqlalchemy import Column, Float, ForeignKey, Enum, Integer, Text, Boolean
from strenum import StrEnum

from config import *
from .base import BaseModelWithId


class MessageTransaction(BaseModelWithId):
    __tablename__ = 'transactions_messages'

    transaction_id = Column(ForeignKey('transactions.id'), nullable = False)
    text = Column(Text, nullable = False)

    from_merchant = Column(Boolean, default = False)
