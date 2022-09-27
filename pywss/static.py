# coding: utf-8
import os

from pywss.statuscode import *


def NewStaticHandler(root, default="application/octet-stream"):
    textHtml = tuple("html,txt,htm,shtml".split(","))
    textCss = tuple("css".split(","))
    textXml = tuple("xml".split(","))
    applicationXJavascript = tuple("js".split(","))
    applicationJson = tuple("json,yml,yaml".split(","))
    imagePng = tuple("jpg,jpeg,png,gif,avif,svg,svgz,wbmp,webp,ico,bmp".split(","))

    def staticHandler(ctx):
        if ctx.headers.get("Content-Range", None):
            ctx.set_status_code(StatusServiceUnavailable)
            ctx.write("Not Support Header Content-Range")
            return
        path = f"{ctx.method}/{ctx.path.strip().strip('/')}".replace(ctx.route, "", 1)
        file = os.path.join(root, *path.split("/"))
        if not os.path.exists(file):
            ctx.set_status_code(StatusNotFound)
            return
        if file.endswith(textHtml):
            ctx.set_content_type("text/html; charset=UTF-8")
        elif file.endswith(textCss):
            ctx.set_content_type("text/css")
        elif file.endswith(applicationXJavascript):
            ctx.set_content_type("application/javascript ")
        elif file.endswith(applicationJson):
            ctx.set_content_type("application/json")
        elif file.endswith(textXml):
            ctx.set_content_type("text/xml")
        elif file.endswith(imagePng):
            ctx.set_content_type("image/png")
        else:
            ctx.set_content_type(default)
        if ctx.method == MethodHead:
            with open(file, "rb") as f:
                ctx.set_content_length(os.stat(f.fileno())[6])
            return
        ctx.write_file(open(file, "rb"))

    return staticHandler
