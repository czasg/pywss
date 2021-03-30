# coding: utf-8
import pywss

from .base import *
from pywss.ctx import Ctx
from service.login import login as sLogin, logout as sLogout
from middleware.jwt import jwt, PAYLOAD

LOGIN_NAME = "name"
LOGIN_PASSWORD = "password"


def login(ctx: Ctx):
    queryParams = ctx.queryParams()
    callback = queryParams.get(PARAMS_CALLBACK)
    responseType = queryParams.get(PARAMS_RESPONSE_TYPE) or "token"

    name = ctx.json().get(LOGIN_NAME)
    password = ctx.json().get(LOGIN_PASSWORD)
    if not name or not password:
        respErr(ctx, "未指定用户/密码")
        return

    if responseType == PARAMS_RESPONSE_TYPE_TOKEN:
        token = sLogin(name, password)
    else:
        respErr(ctx, f"不支持返回类型[{responseType}]")
        return

    if not token:
        respErr(ctx, f"不支持返回类型[{responseType}]")
        return
    if callback:
        ctx.setCookie("Cookie", token)
        ctx.redirect(f"{callback}?token={token}")
    else:
        respOK(ctx, {"token": token})


def logout(ctx: Ctx):
    payload = ctx.getCtxValue(PAYLOAD)
    sLogout(jwt.uid(payload))
    return
