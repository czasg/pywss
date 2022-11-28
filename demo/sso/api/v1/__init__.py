# coding: utf-8
import pywss

from .auth import register as register_auth
from .users import register as register_users


def register(app: pywss.App):
    register_auth(app.party("/auth"))
    register_users(app.party("/users"))
