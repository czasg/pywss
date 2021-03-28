# coding: utf-8
import pywss

from pywss.ctx import Ctx
from service.login import login as sLogin, logout as sLogout
from middleware.jwt import jwt, PAYLOAD


def login(ctx: Ctx):
    data = ctx.json()
    try:
        name = data["name"]
        password = data["password"]
    except:
        ctx.setStatusCode(pywss.StatusBadRequest)
        return
    token = sLogin(name, password)
    if not token:
        ctx.setStatusCode(pywss.StatusBadRequest)
        return
    ctx.write(token)


def logout(ctx: Ctx):
    payload = ctx.getCtxValue(PAYLOAD)
    sLogout(jwt.uid(payload))
    return
