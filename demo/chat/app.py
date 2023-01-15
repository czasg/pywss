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
            uid = f"U-{cls.index}"
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
        # 轮询获取消息
        while True:
            data = ctx.ws_read().decode()  # 阻塞获取
            if data == "ping":  # 心跳数据
                continue
            json_data: dict = json.loads(data)
            msg_type = json_data.get('type')
            if msg_type == "init":
                ctx.ws_write({"type": "init", "uid": uid})
                WebSocketManager.notify({"type": "online", "online": len(WebSocketManager.pool)})
                WebSocketManager.notify({"type": "broad", "uid": "System Admin", "msg": f"欢迎 {uid} 来到WebSocket聊天室！"})
            elif msg_type == "broad":
                WebSocketManager.notify({"type": "broad", "uid": uid, "msg": json_data.get("msg")})
    except:
        pass
    finally:
        WebSocketManager.delete(uid)  # 注销用户
        WebSocketManager.notify({"type": "online", "online": len(WebSocketManager.pool)})
        WebSocketManager.notify({"type": "broad", "uid": "System Admin", "msg": f"{uid} 离开聊天室！"})
        ctx.log.warning(f"{uid} exit")


def main():
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


if __name__ == '__main__':
    main()
    """ 浏览器访问 ctrl+左键
    http://localhost:8080
    http://localhost:8080/static/chat.html
    """
