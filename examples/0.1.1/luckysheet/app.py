# coding: utf-8
import json
import uuid
import pywss
import zlib
import threading
from urllib.parse import unquote


class Pool:
    lock = threading.Lock()
    pool = {}

    @classmethod
    def add(cls, uid, ctx):
        with cls.lock:
            cls.pool[uid] = ctx

    @classmethod
    def delete(cls, uid):
        with cls.lock:
            cls.pool.pop(uid, None)

    @classmethod
    def notify(cls, data, by):
        with cls.lock:
            for uid, ctx in cls.pool.items():  # type: pywss.Context
                if uid == by:
                    continue
                ctx.ws_write(data)


def load(ctx: pywss.Context):
    data = json.dumps([
        {
            "name": "Pywss",
            "index": "sheet_1",
            "order": 0,
            "status": 1,
            "celldata": [],
        }
    ])
    ctx.write(data)


def update(ctx: pywss.Context):
    # 升级 WebSocket
    err = pywss.WebsocketContextWrap(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    uid = str(uuid.uuid4())
    Pool.add(uid, ctx)

    try:
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
                "id": uid,
                "returnMessage": "success",
                "status": 0,
                "type": 3,
                "username": uid,
            }
            if json_data.get("t") != "mv":
                resp_data["type"] = 2
            resp = json.dumps(resp_data).encode()
            Pool.notify(resp, uid)
    except:
        pass
    finally:
        ctx.log.warning(f"{uid} exit")
        Pool.delete(uid)


if __name__ == '__main__':
    app = pywss.App()
    # 注册静态资源
    app.static("/static", ".")
    # 注册 luckysheet 路由
    party = app.party("/luckysheet/api")
    party.post("/loadUrl", load)
    party.get("/updateUrl", update)
    # 启动服务
    app.run()
