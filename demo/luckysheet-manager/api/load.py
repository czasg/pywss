# coding: utf-8
import json
import pywss

from db.mongo import collection as mongodb


def load(ctx: pywss.Context):
    try:
        excel_id = int(ctx.url_params.get("id"))
    except:
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    document = mongodb.find_one({"id": excel_id})
    if not document:
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    data = document["data"]
    ctx.write(json.dumps(data))
