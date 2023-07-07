# coding: utf-8
import pywss


def index(ctx: pywss.Context):
    host = ctx.headers.get("Host")
    if host == "shopping":
        ctx.redirect(f"/static/shopping.html")
    elif host == "living":
        ctx.redirect(f"/static/living.html")
    else:
        ctx.redirect(f"/static/sso.html")


def main(port=8080):
    app = pywss.App()
    app.get("/", index)
    app.static("/static", rootDir="./static")
    app.view_modules("view")
    app.run(port=port)


if __name__ == '__main__':
    main(80)
    """
    http://sso
    http://living
    http://shopping
    """
