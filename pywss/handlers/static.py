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


def newStaticHandler(root, text_html, application_json, default="application/octet-stream"):
    text_html = _ensureToTuple(text_html)
    application_json = _ensureToTuple(application_json)

    def staticHandler(ctx):
        path = ctx.urlParams()["path"]
        file = os.path.join(root, *path.split("/"))
        if os.path.exists(file):
            if file.endswith(text_html):
                ctx.setContentType("text/html")
            elif file.endswith(application_json):
                ctx.setContentType("application/json")
            else:
                ctx.setContentType(default)
            ctx.write(open(file, "rb"))
        else:
            ctx.setStatusCode(StatusNotFound)

    return staticHandler
