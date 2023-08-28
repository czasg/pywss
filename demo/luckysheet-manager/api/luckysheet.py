# coding: utf-8
import json
import uuid
import pywss

from pymongo.collection import ReturnDocument
from db.mongo import collection as mongodb, db
from datetime import datetime


def page(ctx: pywss.Context):
    page_size = int(ctx.url_params.get("page_size", 10))
    page = int(ctx.url_params.get("page", 0))
    skip_count = page * page_size
    documents = mongodb.find().skip(skip_count).limit(page_size).sort("_id", -1)
    return ctx.write({
        "code": 0,
        "message": "ok",
        "data": json.loads(json.dumps(list(documents), default=str)),
    })


def new(ctx: pywss.Context):
    # 创建自增序列
    sequence_doc = db.counters.find_one_and_update(
        {"_id": "luckysheet"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    # 创建新文档
    document = {
        "id": sequence_doc['seq'],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": [
            {
                "name": "Sheet1",
                "index": f"{uuid.uuid4()}",
                "order": 0,
                "status": "1",
                "column": 60,
                "row": 84,
                "config": {},
                "pivotTable": None,
                "isPivotTable": False,
                "data": [[None for _ in range(60)] for _ in range(84)],
                "celldata": [],
                "color": "",
            }
        ]
    }
    mongodb.insert_one(document)
    ctx.write({
        "code": 0,
        "message": "ok",
        "data": json.loads(json.dumps(list(document), default=str)),
    })
