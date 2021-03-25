# coding: utf-8
from .user import *


def registerV1(party):
    party.get("/user")
    party.get("/user/(?P<userId>)")
    party.post("/user/(?P<userId>)")
    party.delete("/user/(?P<userId>)")
    party.patch("/user/(?P<userId>)")
