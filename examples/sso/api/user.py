# coding: utf-8
import service

from .base import *
from middleware.jwt import USER_ID


def getUserList(ctx: Ctx):
    respOK(ctx, service.getUserList())


def getUserInfo(ctx: Ctx):
    uid = ctx.urlParams().get(USER_ID)
    if not uid:
        pass
    respOK(ctx, service.getUserInfo(uid))
