# coding: utf-8
import pywss

from utils.jwt import client as jwt_client


def auth(ctx: pywss.Context):
    bearer = "Bearer "
    authorization = ctx.headers.get("Authorization", "")
    if not authorization.startswith(bearer):
        ctx.set_status_code(pywss.StatusForbidden)
        return
    token = authorization[len(bearer):]
    payload, ok = jwt_client.verify(token)
    if not ok:
        ctx.set_status_code(pywss.StatusForbidden)
        return
    ctx.data.username = payload.get("une")
    ctx.next()
