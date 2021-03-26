# coding: utf-8
import uuid
import time

from pywss.ctx import Ctx

X_TRACE_ID = "X-Trace-Id"


def trace(ctx: Ctx):
    XTraceID = ctx.headers().get(X_TRACE_ID, f"{uuid.uuid4()}-{time.time()}")
    log = ctx.log().withFields({"XTraceID": XTraceID})
    ctx.setLog(log)
    ctx.setCtxValue(X_TRACE_ID, XTraceID)
    ctx.next()
