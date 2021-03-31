# coding: utf-8
import pywss

from pywss.ctx import Ctx
from pywss.statuscode import StatusForbidden
from jwt import jwt, Authorization, PAYLOAD

USER_ID = "userID"


def jwtCheck(ctx: Ctx):
    token = ctx.headers().get(Authorization)
    if not token:
        ctx.setStatusCode(pywss.StatusUnauthorized)
        return
    payload, ok = jwt.valid(token)
    if not ok:
        ctx.setStatusCode(pywss.StatusUnauthorized)
        return
    ctx.setCtxValue(PAYLOAD, payload)
    ctx.next()


def justAdmin(ctx: Ctx):
    payload = ctx.getCtxValue(PAYLOAD)
    if jwt.adm(payload):
        ctx.next()
    else:
        ctx.setStatusCode(StatusForbidden)


def justAdminOrUserSelf(ctx: Ctx):
    payload = ctx.getCtxValue(PAYLOAD)
    if jwt.adm(payload):
        ctx.next()
    elif ctx.urlParams().get(USER_ID) == jwt.uid(payload):
        ctx.next()
    else:
        ctx.setStatusCode(StatusForbidden)
