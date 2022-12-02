# coding: utf-8
import json
import pywss

from db.mongo import collection as mongodb


def load(ctx: pywss.Context):
    document = mongodb.find_one({"name": "luckysheet"})
    data = document["data"]
    ctx.write(json.dumps(data))
