# coding: utf-8
from pywss.route import Route

from middleware.jwt import *
from .user import *
from .login import *
from .auth import *

"""
v1:
|-> GET/user 获取用户列表
|-> POST/user 创建新用户
|-> GET/user/(?P<userID>) 获取用户详情
|-> PUT/user/(?P<userID>) 更新用户信息
|-> PATCH/user/(?P<userID>) 更新用户局部信息
|-> DELETE/user/(?P<userID>) 删除用户

v2:
|-> POST/user/login 用户登录，发放token
|-> POST/user/logout 用户注销，调用回调接口

v3:
|-> GET/secret 获取秘钥列表
|-> GET/secret/(?P<secretID>) 获取秘钥详情
|-> POST/secret 创建秘钥（用户秘钥、接口秘钥）
|-> POST/oauth2 用户凭证、秘钥认证
"""


def registerAPI(app: Route):
    registerV1(app.party("/v1", jwtCheck))
    registerV2(app.party("/v2"))
    registerV3(app.party("/v3"))


def registerV1(app: Route):
    app.get("/user", justAdmin, getUserList)
    app.post("/user", justAdmin)
    app.get("/user/(?P<userID>)", justAdminOrUserSelf)
    app.put("/user/(?P<userID>)", justAdminOrUserSelf)
    app.patch("/user/(?P<userID>)", justAdminOrUserSelf)
    app.delete("/user/(?P<userID>)", justAdmin)


def registerV2(app: Route):
    app.post("/user/login", login)
    app.post("/user/logout", jwtCheck)


def registerV3(app: Route):
    pass
