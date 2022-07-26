from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Transaction
from .base import BaseModel


class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, nullable = False, unique = True, primary_key = True)

    language = Column(Text, nullable = False)
    username = Column(Text, nullable = False, unique = True)
    first_name = Column(Text, nullable = False)
    last_name = Column(Text, nullable = False)

    phone = Column(Text, nullable = True, unique = True)
    auth = Column(Boolean, default = False)

    good_transactions = Column(Integer, default = 0)
    bad_transactions = Column(Integer, default = 0)

    ban_time = Column(Integer, default = 0)

    transactions = relationship(Transaction, backref = 'user', lazy = 'select')
