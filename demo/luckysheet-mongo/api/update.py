# coding: utf-8
import json
import pywss
import zlib

from service.update import lucky_sheet_queue
from urllib.parse import unquote
from utils.ws import manager


def prepare(ctx: pywss.Context):
    # 升级 WebSocket
    err = pywss.WebSocketUpgrade(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    # 注册并获取用户ID
    ctx.data.uid = manager.register(ctx)
    try:
        ctx.next()
    except:
        pass
    finally:
        ctx.log.warning(f"{ctx.data.uid} exit")
        manager.delete(ctx.data.uid)


def loop(ctx: pywss.Context):
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
            "username": ctx.data.uid,
        }
        if json_data.get("t") != "mv":
            resp_data["type"] = 2
            lucky_sheet_queue.put(json_data)  # luckysheet数据存储至数据库
        resp = json.dumps(resp_data).encode()
        manager.notify(resp, ctx.data.uid)
