# coding: utf-8
import pywss

from . import load
from . import update


def register(app: pywss.App):
    app.post("/luckysheet/api/loadUrl", load.load)
    app.get("/luckysheet/api/updateUrl", update.prepare, update.loop)
