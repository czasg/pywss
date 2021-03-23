# coding: utf-8
from pywss.websocket import *


def WebSocketHandler(ctx):
    if ctx.headers().get("Upgrade") != "websocket":
        return
    secKey = ctx.headers().get("Sec-Websocket-Key")
    if not secKey:
        return
    secResp = createWebSocketResponse(secKey)
    ctx.streamWriter().write(secResp)
    ctx.wsFill()
    ctx.next()
    while True:
        ctx.wsFill()
        ctx.handler()(ctx)
