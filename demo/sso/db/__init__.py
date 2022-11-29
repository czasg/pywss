# coding: utf-8
import os
from .model import base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine(os.environ.get("MYSQL_URI", "mysql+pymysql://root:123456@localhost:3306/sso"))
base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))
