# coding: utf-8
from pywss.route import Route
from pywss.wsgi import run


class Pywss(Route):

    def run(self, host="0.0.0.0", port=8080):
        run(host, port)


if __name__ == '__main__':
    app = Pywss()
    app.get("/api/fos-internal-api/v1/query", lambda ctx: print(ctx.body(), ctx.write("Get hello world")))
    app.post("/api/fos-internal-api/v1/query", lambda ctx: print(ctx.body(), ctx.write("Post hello world")))
    app.get("/baidu", lambda ctx: print(ctx.redirect("/api/fos-internal-api/v1/query")))
    app.post("/baidu", lambda ctx: print(ctx.redirect("/api/fos-internal-api/v1/query")))
    app.handleDir("/download")
    app.run()
