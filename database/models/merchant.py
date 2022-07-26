from sqlalchemy import Column, Integer, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from . import Transaction
from .base import BaseModel


class Merchant(BaseModel):
    __tablename__ = 'merchants'

    id = Column(ForeignKey('users.id'), nullable = False, unique = True, primary_key = True)

    accumulated_commission = Column(Float, default = 0)

    good_transactions = Column(Integer, default = 0)
    bad_transactions = Column(Integer, default = 0)
    rating = Column(Integer, default = 0)

    transactions = relationship(Transaction, backref = 'merchant', lazy = 'select')
