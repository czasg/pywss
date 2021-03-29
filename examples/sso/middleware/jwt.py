# coding: utf-8
import pywss

from pywss.ctx import Ctx
from jwt import jwt, Authorization, PAYLOAD


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
