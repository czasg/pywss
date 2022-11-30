# coding: utf-8
import os

from pywss.statuscode import StatusNotFound, StatusServiceUnavailable, MethodHead


def html_template(path, limit):
    count = 0
    dirs = []
    files = []
    for el in os.scandir(path):
        name = el.name
        if len(name) > 8:
            name = name[:8] + "..."
        if el.is_dir():
            dirs.append(f'<a class="box box-dir" title="目录：{el.name}" href="{el.name}/">{name}</a>')
        else:
            files.append(f'<a class="box box-file" '
                         f'title="文件名：{el.name}\n文件大小：{el.stat().st_size}" href="{el.name}">{name}</a>')
        count += 1
        if count >= limit:
            break
    data = "\n".join(dirs) + "\n".join(files)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Pywss Server</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100vw;
            overflow-x: hidden;
            display: flex;
            flex-wrap: wrap;
        }}
        .box {{
            margin: 15px;
            width: 100px;
            height: 100px;
            border-radius: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            font-weight: bold;
            color: #f1f1f1;
            text-decoration: none;
        }}
        .box:hover {{
            box-shadow: 0 0 8px 6px #7f7a7a;
            cursor: pointer;
        }}
        .box-dir {{
            background: #4495dc;
        }}
        .box-file {{
            background: #656668;
        }}
    </style>
</head>
<body>
<div class="container">
    {data}
</div>
</body>
</html>
"""


def NewStaticHandler(root, default="application/octet-stream", limit=100):
    textHtml = tuple("html,htm,shtml".split(","))
    textPlain = tuple("py,go,md,txt".split(","))
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
        _path = ctx.path.split('?', 1)[0]
        path = f"GET{_path}"[len(ctx.route):].strip("/")
        file = os.path.join(root, *path.split("/"))
        if not os.path.exists(file):
            ctx.set_status_code(StatusNotFound)
            return
        if os.path.isdir(file):
            if _path[-1] != "/":
                ctx.redirect(_path + "/")
                return
            ctx.set_content_type("text/html; charset=UTF-8")
            ctx.write(html_template(file, limit))
            return
        if file.endswith(textHtml):
            ctx.set_content_type("text/html; charset=UTF-8")
        elif file.endswith(textPlain):
            ctx.set_content_type("text/plain; charset=UTF-8")
        elif file.endswith(textCss):
            ctx.set_content_type("text/css")
        elif file.endswith(applicationXJavascript):
            ctx.set_content_type("application/javascript")
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
