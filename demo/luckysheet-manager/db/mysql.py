# coding: utf-8
from .model import base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine("sqlite:///sqlite.db", echo=True)
base.metadata.create_all(engine)
Sess = scoped_session(sessionmaker(bind=engine))


class Session:

    def __enter__(self):
        self.sess = Sess()
        return self.sess

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sess.rollback()
