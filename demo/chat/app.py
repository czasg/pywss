# coding: utf-8
import json
import pywss
import threading


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
    def notify(cls, data):
        with cls.lock:
            for uid, ctx in cls.pool.items():  # type: pywss.Context
                try:
                    ctx.ws_write(data)
                except:
                    cls.pool.pop(uid, None)


def handler(ctx: pywss.Context):
    # 升级 WebSocket
    err = pywss.WebSocketUpgrade(ctx)
    if err:
        ctx.log.error(err)
        ctx.set_status_code(pywss.StatusBadRequest)
        return
    # 注册并获取用户ID
    uid = WebSocketManager.register(ctx)
    try:
        # 首次连接
        data = ctx.ws_read().decode()
        json_data = json.loads(data)
        if json_data.get('start') == True:
            ctx.ws_write({'sock_id': uid})  # 赋值用户名
            WebSocketManager.notify({'online': len(WebSocketManager.pool)})  # 首次进来，广播一轮在线人数
        # 轮询获取消息
        while True:
            data = ctx.ws_read().decode()  # 阻塞获取
            json_data = json.loads(data)
            msg = json_data.get('msg')
            if msg:
                WebSocketManager.notify({'from': uid, 'msg': msg})  # 广播消息
    except:
        pass
    finally:
        WebSocketManager.delete(uid)  # 注销用户
        WebSocketManager.notify({'online': len(WebSocketManager.pool)})  # 用户退出，广播一轮在线人数
        WebSocketManager.notify({'from': uid, 'msg': "拜拜~"})
        ctx.log.warning(f"{uid} exit")


if __name__ == '__main__':
    # 初始化 app
    app = pywss.App()
    # 注册静态路由
    app.static("/static", ".")
    # 注册 websocket 路由
    app.get("/ws/chat", handler)
    # 注册首页路由
    app.get("/", lambda ctx: ctx.redirect("/static/chat.html"))
    # 启动服务
    app.run()
    """ 浏览器访问 ctrl+左键
    http://localhost:8080
    http://localhost:8080/static/chat.html
    """
