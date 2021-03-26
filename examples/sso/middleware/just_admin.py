# coding: utf-8
from pywss.ctx import Ctx
from pywss.statuscode import StatusForbidden

from jwt import jwt, PAYLOAD


def justAdmin(ctx: Ctx):
    payload = ctx.getCtxValue(PAYLOAD)
    if jwt.adm(payload):
        ctx.next()
    else:
        ctx.setStatusCode(StatusForbidden)
