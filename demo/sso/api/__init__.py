# coding: utf-8
import pywss

from .v1 import register as register_v1


def register(app: pywss.App):
    register_v1(app.party("/api/v1"))
