# coding: utf-8
from pywss.statuscode import MethodOptions


def NewCORSHandler(
        allow_origins: tuple = ("*",),
        allow_methods: tuple = ("DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT",),
        allow_headers: tuple = ("Accept", "Accept-Language", "Content-Language", "Content-Type",),
        allow_credentials: bool = True,
):
    allowOrigins = ",".join(allow_origins)
    allowMethods = ",".join(allow_methods)
    allowHeaders = ",".join(allow_headers)
    allowCredentials = "true" if allow_credentials else "false"

    def cors(ctx):
        if ctx.method == MethodOptions:
            ctx.set_header("Access-Control-Allow-Origin", allowOrigins)
            ctx.set_header("Access-Control-Allow-Methods", allowMethods)
            ctx.set_header("Access-Control-Expose-Headers", allowHeaders)
            ctx.set_header("Access-Control-Allow-Credentials", allowCredentials)
            return
        ctx.next()

    return cors
