# coding: utf-8
from .user import *
from .login import *
from .auth import *
from pywss.route import Route
from middleware.just_admin import justAdmin
from middleware.jwt import jwtCheck


def registerAPI(app: Route):
    app.post("/user/login", login)  # 用户登录

    registerJWT(app.party("", jwtCheck))  # 注册JWT中间件


def registerJWT(app: Route):
    app.post("/user/logout", logout)  # 用户注销
    app.post("/user/auth")  # 用户认证
    app.get("/user/(?P<userID>)")  # 用户详情信息
    registerAdmin(app.party("", justAdmin))  # 注册Admin中间件


def registerAdmin(app: Route):
    app.get("/user", getUserList)  # 用户列表
    app.post("/user")  # 用户注册
    app.post("/user/(?P<userID>)")  # 编辑用户
    app.delete("/user/(?P<userID>)")  # 用户删除
