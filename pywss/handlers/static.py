# coding: utf-8
import os

from pywss.statuscode import StatusNotFound


def _ensureToTuple(value):
    if isinstance(value, str):
        return tuple(value.split(","))
    elif isinstance(value, list):
        return tuple(value)
    elif isinstance(value, tuple):
        return value
    return ()


def newStaticHandler(
        root,
        textHtml,
        textCss,
        applicationXJavascript,
        applicationJson,
        imagePng,
        default="application/octet-stream"
):
    textHtml = _ensureToTuple(textHtml)
    textCss = _ensureToTuple(textCss)
    applicationXJavascript = _ensureToTuple(applicationXJavascript)
    applicationJson = _ensureToTuple(applicationJson)
    imagePng = _ensureToTuple(imagePng)

    def staticHandler(ctx):
        path = ctx.urlParams()["path"]
        file = os.path.join(root, *path.split("/"))
        if os.path.exists(file):
            if file.endswith(textHtml):
                ctx.setContentType("text/html")
            elif file.endswith(textCss):
                ctx.setContentType("text/css")
            elif file.endswith(applicationXJavascript):
                ctx.setContentType("application/x-javascript")
            elif file.endswith(applicationJson):
                ctx.setContentType("application/json")
            elif file.endswith(imagePng):
                ctx.setContentType("image/png")
            else:
                ctx.setContentType(default)
            ctx.write(open(file, "rb"))
        else:
            ctx.setStatusCode(StatusNotFound)

    return staticHandler
