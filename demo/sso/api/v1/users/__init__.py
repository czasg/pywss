# coding: utf-8
import pywss
import hashlib

from db import Session
from db.model import User
from utils.const import Response
from utils.jwt import client as jwt_client
from wall.auth import auth as wall_auth


def register(app: pywss.App):
    # 获取用户列表
    app.get("/", wall_auth, get_users)
    # 注册用户
    app.post("/", post_users)
    # 用户登录
    app.post("/login", post_users_login)


def get_users(ctx: pywss.Context):
    resp = Response()
    page_size = int(ctx.params.get("page_size", 10))
    page_num = int(ctx.params.get("page_num", 0))
    with Session() as session:
        resp.data = []
        for uid, alias, username in session.query(User.id, User.alias, User.username). \
                order_by(User.id). \
                limit(page_size). \
                offset(page_num). \
                all():
            resp.data.append({
                "id": uid,
                "alias": alias,
                "username": username,
            })
        ctx.write(resp)


def post_users(ctx: pywss.Context):
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


def post_users_login(ctx: pywss.Context):
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
        token = jwt_client.generate(user.username)
        ctx.set_cookie("jwt_token", token, maxAge=3600)
        ctx.write(resp)
