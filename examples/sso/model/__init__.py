# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base
from .user import User

engine = create_engine("postgres+psycopg2://postgres:postgres@localhost:5432/sso")

# import os
# DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sso.db")
# engine = create_engine(f"sqlite:///{DB_FILE}")


DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
