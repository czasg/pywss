# coding: utf-8
import hashlib
from dao.user import *
from jwt import jwt


def login(name, password):
    user = getUserByName(name)
    if not user:
        return

    if hashlib.md5(password.encode()).hexdigest() != user.password:
        return

    return {"token": jwt.create(user.id, user.name, user.role_id)}


def logout(uid):
    user = getUserByID(uid)
    if not user:
        return

    updateUser(uid, login_at=0)
