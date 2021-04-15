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
    ctx.streamWriter().flush()
    cid = ctx.streamWriterFileno()
    wsPool.add(cid, ctx)
    try:
        ctx.wsFill()
        ctx.next()
        while True:
            if not ctx.wsFill():
                continue
            ctx.handler()(ctx)
    except:
        pass
    wsPool.delete(cid)
