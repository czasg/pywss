# coding: utf-8
import os

from pywss.statuscode import StatusNotFound

textHtml = tuple("html,txt,htm,shtml".split(","))
textCss = tuple("css".split(","))
textXml = tuple("xml".split(","))
applicationXJavascript = tuple("js".split(","))
applicationJson = tuple("json,yml,yaml".split(","))
imagePng = tuple("jpg,jpeg,png,gif,avif,svg,svgz,wbmp,webp,ico,bmp".split(","))


def NewStaticHandler(root, default="application/octet-stream"):
    def staticHandler(ctx):
        path = f"{ctx.method}/{ctx.path.strip().strip('/')}".replace(ctx.route, "", 1)
        file = os.path.join(root, *path.split("/"))
        if not os.path.exists(file):
            ctx.set_status_code(StatusNotFound)
            return
        if file.endswith(textHtml):
            ctx.set_content_type("text/html")
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
        ctx.write_file(open(file, "rb"))

    return staticHandler
