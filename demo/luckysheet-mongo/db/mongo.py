# coding: utf-8
import pymongo

conn = pymongo.MongoClient(f"mongodb://root:root@localhost:27017/admin")
db = conn["luckysheet"]
collection = db["luckysheet"]
