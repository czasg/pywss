# coding: utf-8
import uuid
import json
import pywss
import threading


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
    def notify(cls, data):
        with cls.lock:
            for uid, ctx in cls.pool.items():  # type: pywss.Context
                ctx.ws_write(data)


def handler(ctx: pywss.Context):
    print(ctx.data.name)
    # 升级 WebSocket
    err = pywss.WebSocketUpgrade(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    uid = str(uuid.uuid4())
    Pool.add(uid, ctx)
    try:
        # 首次连接
        data = ctx.ws_read().decode()
        json_data = json.loads(data)
        if json_data.get('start') == True:
            ctx.ws_write({'sock_id': uid})  # 用户名
            Pool.notify({'online': len(Pool.pool)})  # 在线人数
        # 获取消息
        while True:
            data = ctx.ws_read().decode()  # 阻塞获取
            json_data = json.loads(data)
            msg = json_data.get('msg')
            if msg:
                Pool.notify({'from': uid, 'msg': msg})  # 消息
    except:
        pass
    finally:
        ctx.log.warning(f"{uid} exit")
        Pool.delete(uid)

    with ctx.log.trycache():
        Pool.notify({'online': len(Pool.pool)})
        Pool.notify({'from': uid, 'msg': "拜拜~"})


if __name__ == '__main__':
    # 初始化 app
    app = pywss.App()
    # 注册静态路由
    app.static("/static", ".")
    # 注册 websocket 路由
    app.get("/ws/chat", handler)
    # 注册首页路由
    app.any("/", lambda ctx: ctx.redirect("/static/chat.html"))
    # 启动服务
    app.run()
    """ 浏览器访问 ctrl+左键
    http://localhost:8080
    http://localhost:8080/static/chat.html
    """
