# coding: utf-8
import pywss

from wall.auth import auth as wall_auth


def register(app: pywss.App):
    # 三方登录接口
    app.get("/", auth)
    # 三方校验接口
    app.post("/verify", wall_auth, post_verify)


def auth(ctx: pywss.Context):
    ref = ctx.url_params.get("callback") or ctx.headers.get("Referer")
    if not ref:
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    ctx.redirect(f"http://sso/static/login.html?callback={ref}")


def post_verify(ctx: pywss.Context):
    ctx.set_status_code(pywss.StatusNoContent)
