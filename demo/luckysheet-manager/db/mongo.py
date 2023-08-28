# coding: utf-8
import pymongo

conn = pymongo.MongoClient()
db = conn["luckysheet"]
collection = db["luckysheet"]
