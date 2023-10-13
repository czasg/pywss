# coding: utf-8
import pywss
import hashlib

from db.mysql import Session
from db.model import User
from utils.constant import Response


def register(ctx: pywss.Context):
    resp = Response()
    req: dict = ctx.json()
    alias = req.get("alias")
    username = req.get("username")
    password = req.get("password")
    if not all((alias, username, password)):
        resp.code = 40000
        resp.msg = "must provide an alias & username & password"
        ctx.write(resp)
        return
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    password = sha256.hexdigest()
    with Session() as session:
        if session.query(User.id).filter(User.username == username).count() > 0:
            resp.code = 40000
            resp.msg = f"username[{username}] exists"
            ctx.write(resp)
            return
        user = User(alias=alias, username=username, password=password)
        session.add(user)
        session.commit()
        ctx.write(resp)


def login(ctx: pywss.Context):
    resp = Response()
    req: dict = ctx.json()
    username = req.get("username")
    password = req.get("password")
    if not all((username, password)):
        resp.code = 40000
        resp.msg = "must provide an account number and password"
        ctx.write(resp)
        return
    sha256 = hashlib.sha256()
    sha256.update(password.encode())
    password = sha256.hexdigest()
    with Session() as session:
        user = session.query(User).filter(User.username == username).limit(1).scalar()
        if not user:
            resp.code = 40000
            resp.msg = f"username[{username}] not exists"
            ctx.write(resp)
            return
        if user.password != password:
            resp.code = 40000
            resp.msg = f"incorrect password"
            ctx.write(resp)
            return
        token = ctx.data.jwt.encrypt(uid=user.id, alias=user.alias, username=user.username)
        ctx.set_cookie("jwt_token", token, maxAge=3600)
        ctx.write(resp)
