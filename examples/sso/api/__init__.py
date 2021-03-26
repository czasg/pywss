# coding: utf-8
from middleware.just_admin import justAdmin


def registerAPI(app):
    # 用户登录
    app.post("/user/login")
    # 用户注销
    app.post("/user/logout")
    # 用户认证
    app.post("/user/auth")
    # 用户详情信息
    app.get("/user/info")
    # Admin用户专用
    registerAdmin(app.party("", justAdmin))


def registerAdmin(app):
    # 获取用户列表详情
    app.get("/user/list")
    # 删除用户
    app.delete("/user")
