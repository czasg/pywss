# coding: utf-8
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
from .user import User

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sso.db")
engine = create_engine(f"sqlite:///{DB_FILE}")
DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
