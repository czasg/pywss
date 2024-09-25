# coding: utf-8
import pywss

from pywss.constant import *


def NewCORSHandler(
        allow_origins: tuple = ("*",),
        allow_methods: tuple = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"),
        allow_headers: tuple = ("*",),
        allow_credentials: bool = True,
):
    allowOrigins = ",".join(allow_origins)
    allowMethods = ",".join(allow_methods)
    allowHeaders = ",".join(allow_headers)
    allowCredentials = "true" if allow_credentials else "false"

    def corsHandler(ctx: pywss.Context):
        headerOrigin = ctx.headers.get(HeaderOrigin, "")
        useLocal = "localhost" in headerOrigin
        origin = headerOrigin if useLocal else allowOrigins
        ctx.set_header(HeaderAccessControlAllowOrigin, origin)
        ctx.set_header(HeaderAccessControlAllowMethods, allowMethods)
        ctx.set_header(HeaderAccessControlAllowHeaders, allowHeaders)
        ctx.set_header(HeaderAccessControlAllowCredentials, allowCredentials)
        if ctx.method == MethodOptions:
            return
        ctx.next()

    return corsHandler
