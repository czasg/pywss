# coding: utf-8
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

base = declarative_base()


class User(base):
    __tablename__ = 'users'

    id = Column(Integer(), autoincrement=True, primary_key=True)
    alias = Column(Text())
    username = Column(Text())
    password = Column(Text())
