# coding: utf-8
from sqlalchemy import Column, String, Integer, Text
from .base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(20))
    password = Column(String(64))
    create_at = Column(Integer)
    update_at = Column(Integer)
    login_at = Column(Integer)
    role_id = Column(Integer, default=1)
    meta = Column(Text)
