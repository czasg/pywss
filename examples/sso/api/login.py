# coding: utf-8
from .base import *
from pywss.ctx import Ctx
from service.login import *
from middleware.jwt import jwt, PAYLOAD

LOGIN_NAME = "name"
LOGIN_PASSWORD = "password"


def login(ctx: Ctx):
    queryParams = ctx.queryParams()
    callback = queryParams.get(PARAMS_CALLBACK)

    name = ctx.json().get(LOGIN_NAME)
    password = ctx.json().get(LOGIN_PASSWORD)
    if not name or not password:
        respErr(ctx, "未指定用户/密码")
        return

    token = loginService(name, password)

    if callback:
        ctx.setCookie("Cookie", token)
        ctx.redirect(f"{callback}?token={token}")
    else:
        respOK(ctx, {"token": token})


def logout(ctx: Ctx):
    pass
