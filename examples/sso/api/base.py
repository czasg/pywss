# coding: utf-8
from pywss.ctx import Ctx

PARAMS_CALLBACK = "callback"
PARAMS_RESPONSE_TYPE = "response_type"
PARAMS_RESPONSE_TYPE_TOKEN = "token"


def respOK(ctx: Ctx, data, msg=""):
    ctx.write({
        "code": 10000,
        "msg": msg,
        "data": data,
    })


def respErr(ctx: Ctx, msg, data):
    ctx.write({
        "code": 99999,
        "msg": msg,
        "data": data,
    })
