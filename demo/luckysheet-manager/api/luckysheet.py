# coding: utf-8
import json
import pywss
import zlib

from db.mongo import collection as mongodb
from service.update import lucky_sheet_queue
from urllib.parse import unquote
from utils.ws import manager


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


def prepare(ctx: pywss.Context):
    try:
        excel_id = int(ctx.url_params.get("id"))
    except:
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    # 升级 WebSocket
    err = pywss.WebSocketUpgrade(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    # 注册并获取用户ID
    ctx.data.excel_id = excel_id
    ctx.data.uid = manager.register(ctx, excel_id)
    try:
        ctx.next()
    except:
        pass
    finally:
        ctx.log.warning(f"{ctx.data.uid} exit")
        manager.delete(ctx.data.uid, excel_id)


def loop(ctx: pywss.Context):
    excel_id = ctx.data.excel_id
    uid = ctx.data.uid
    username = ctx.data.jwt_payload.get('alias', uid)
    # 轮询获取消息
    while True:
        data = ctx.ws_read()
        if data == b"rub":  # 心跳检测
            continue
        data_raw = data.decode().encode('iso-8859-1')  # 转编码
        data_unzip = unquote(zlib.decompress(data_raw, 16).decode())  # 解压缩
        json_data = json.loads(data_unzip)
        resp_data = {
            "data": data_unzip,
            "id": ctx.data.uid,
            "returnMessage": "success",
            "status": 0,
            "type": 3,
            "username": username,
        }
        if json_data.get("t") != "mv":
            resp_data["type"] = 2
            lucky_sheet_queue.put((excel_id, json_data))  # luckysheet数据存储至数据库
        resp = json.dumps(resp_data).encode()
        manager.notify(resp, uid, excel_id)
