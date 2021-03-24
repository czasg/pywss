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


def newStaticHandler(root, textHtml, applicationJson, imageGif, default="application/octet-stream"):
    textHtml = _ensureToTuple(textHtml)
    applicationJson = _ensureToTuple(applicationJson)
    imageGif = _ensureToTuple(imageGif)

    def staticHandler(ctx):
        path = ctx.urlParams()["path"]
        file = os.path.join(root, *path.split("/"))
        if os.path.exists(file):
            if file.endswith(textHtml):
                ctx.setContentType("text/html")
            elif file.endswith(applicationJson):
                ctx.setContentType("application/json")
            elif file.endswith(imageGif):
                ctx.setContentType("image/gif")
            else:
                ctx.setContentType(default)
            ctx.write(open(file, "rb"))
        else:
            ctx.setStatusCode(StatusNotFound)

    return staticHandler
