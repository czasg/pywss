# coding: utf-8
import json
import pywss
import zlib
import threading

from urllib.parse import unquote


class WebSocketManager:
    lock = threading.Lock()
    pool = {}
    index = 0

    @classmethod
    def register(cls, ctx):
        with cls.lock:
            cls.index += 1
            uid = f"user-{cls.index}"
            cls.pool[uid] = ctx
            return uid

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
                try:
                    ctx.ws_write(data)
                except:
                    cls.pool.pop(uid, None)


def load(ctx: pywss.Context):
    data = json.dumps([
        {
            "name": "Sheet1",
            "index": f"sheet_01",
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
    ])
    ctx.write(data)


def update(ctx: pywss.Context):
    # 升级 WebSocket
    err = pywss.WebSocketUpgrade(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    # 注册并获取用户ID
    uid = WebSocketManager.register(ctx)
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
            WebSocketManager.notify(resp, uid)
    except:
        pass
    finally:
        ctx.log.warning(f"{uid} exit")
        WebSocketManager.delete(uid)


def main():
    # 初始化 app
    app = pywss.App()
    # 注册静态资源
    app.get("/", lambda ctx: ctx.redirect("/static/luckysheet.html"))
    app.static("/static", "./static")
    # 注册 luckysheet 路由
    app.post("/luckysheet/api/loadUrl", load)
    app.get("/luckysheet/api/updateUrl", update)
    # 启动服务
    app.run()


if __name__ == '__main__':
    main()
    """ 浏览器访问 ctrl+左键
    http://localhost:8080
    http://localhost:8080/static/luckysheet.html
    """
