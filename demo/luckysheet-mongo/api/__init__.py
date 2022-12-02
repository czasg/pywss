# coding: utf-8
import pywss

from . import load
from . import update


def register(app: pywss.App):
    app.post("/loadUrl", load.load)
    app.get("/updateUrl", update.prepare, update.loop)
