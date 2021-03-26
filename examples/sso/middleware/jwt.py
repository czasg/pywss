# coding: utf-8
from pywss.ctx import Ctx


def jwtCheck(ctx: Ctx):
    ctx.next()
