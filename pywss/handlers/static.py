# coding: utf-8
import os

from pywss.statuscode import StatusNotFound


def newStaticHandler(root):
    def staticHandler(ctx):
        ctx.setContentType("application/octet-stream")
        path = ctx.urlParams()["path"]

        file = os.path.join(root, *path.split("/"))
        if os.path.exists(file):
            ctx.write(open(file, "rb"))
        else:
            ctx.setStatusCode(StatusNotFound)

    return staticHandler
