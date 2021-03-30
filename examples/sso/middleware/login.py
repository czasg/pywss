# coding: utf-8
from pywss.ctx import Ctx


def checkLogin(ctx: Ctx):
    ctx.next()
