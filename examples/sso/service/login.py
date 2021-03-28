# coding: utf-8
import hashlib
from dao.user import getUserByName
from jwt import jwt


def login(name, password):
    user = getUserByName(name)
    if not user:
        return

    if hashlib.md5(password.encode()).hexdigest() != user.Password:
        return

    return jwt.create(user.Id, user.Name, user.Name == "root")
