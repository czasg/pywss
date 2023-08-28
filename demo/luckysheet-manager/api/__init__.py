# coding: utf-8
import pywss

from . import load
from . import luckysheet
from . import update


def register(app: pywss.App):
    app.get("/luckysheet", luckysheet.page)
    app.post("/luckysheet", luckysheet.new)
    app.post("/luckysheet/api/loadUrl", load.load)
    app.get("/luckysheet/api/updateUrl", update.prepare, update.loop)
