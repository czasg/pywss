# coding: utf-8
import dao
import hashlib

from jwt import jwt


def login(name, password):
    user = dao.getUserByName(name)
    if not user:
        return

    if hashlib.md5(password.encode()).hexdigest() != user.password:
        return

    return {"token": jwt.create(user.id, user.name, user.role_id)}


def logout(uid):
    pass
