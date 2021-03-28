# coding: utf-8
import time
import loggus

from typing import List
from model import DBSession
from model.user import User


def getAllUsers() -> List[User]:
    session = DBSession()
    try:
        return session.query(User).all()
    except:
        loggus.withFieldTrace().error("Add User Err")
    finally:
        session.close()


def getUserByID(uid: int) -> User:
    session = DBSession()
    try:
        return session.query(User).filter_by(id=uid).one()
    except:
        loggus.withFieldTrace().error("Add User Err")
    finally:
        session.close()


def getUserByName(name: str) -> User:
    session = DBSession()
    try:
        return session.query(User).filter_by(name=name).one()
    except:
        loggus.withFieldTrace().error("Add User Err")
    finally:
        session.close()


def addUser(name, pwd, meta) -> User:
    session = DBSession()
    try:
        now = int(time.time())
        user = User(name=name, password=pwd, meta=meta,
                    create_at=now, update_at=now, login_at=now)
        session.add(user)
        session.commit()
        return user
    except:
        loggus.withFieldTrace().error("Add User Err")
    finally:
        session.close()


def delUserByID(uid: int) -> User:
    session = DBSession()
    try:
        user = User(id=uid)
        session.delete(user)
        session.commit()
        return user
    except:
        loggus.withFieldTrace().error("Add User Err")
    finally:
        session.close()


def updateUser(uid: int, **kwargs):
    session = DBSession()
    try:
        session.query(User).filter_by(id=uid).update(kwargs)
        session.commit()
    except:
        loggus.withFieldTrace().error("Add User Err")
    finally:
        session.close()
