# coding: utf-8
import pywss

from . import luckysheet
from . import manager
from . import user


def register(app: pywss.App):
    app.post("/api/v1/user/login", user.login)
    app.post("/api/v1/user/register", user.register)
    app.get("/api/v1/luckysheet", manager.page)
    app.post("/api/v1/luckysheet", manager.new)
    app.post("/api/v1/luckysheet/loadUrl", luckysheet.load)
    app.get("/api/v1/luckysheet/updateUrl", luckysheet.prepare, luckysheet.loop)
