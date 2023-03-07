# coding: utf-8
import json
import pywss
import threading


class WebSocketView:

    def __init__(self):
        self.lock = threading.Lock()
        self.pool = {}
        self.index = 0

    def register(self, ctx):
        with self.lock:
            self.index += 1
            uid = f"user-{self.index}"
            self.pool[uid] = ctx
            return uid

    def delete(self, uid):
        with self.lock:
            self.pool.pop(uid, None)

    def notify(self, data):
        with self.lock:
            for uid, ctx in self.pool.items():  # type: pywss.Context
                try:
                    ctx.ws_write(data)
                except:
                    self.pool.pop(uid, None)

    def http_get(self, ctx: pywss.Context):
        # 升级 WebSocket
        err = pywss.WebSocketUpgrade(ctx)
        if err:
            ctx.log.error(err)
            ctx.set_status_code(pywss.StatusBadRequest)
            return
        # 注册并获取用户ID
        uid = self.register(ctx)
        try:
            # 首次连接
            data = ctx.ws_read().decode()
            json_data = json.loads(data)
            if json_data.get('start') == True:
                ctx.ws_write({'sock_id': uid})  # 赋值用户名
                self.notify({'online': len(self.pool)})  # 首次进来，广播一轮在线人数
            # 轮询获取消息
            while True:
                data = ctx.ws_read().decode()  # 阻塞获取
                json_data = json.loads(data)
                msg = json_data.get('msg')
                if msg:
                    self.notify({'from': uid, 'msg': msg})  # 广播消息
        except:
            pass
        finally:
            self.delete(uid)  # 注销用户
            self.notify({'online': len(self.pool)})  # 用户退出，广播一轮在线人数
            self.notify({'from': uid, 'msg': "拜拜~"})
            ctx.log.warning(f"{uid} exit")


def main():
    # 初始化 app
    app = pywss.App()
    # 注册静态路由
    app.static("/static", ".")
    # 注册 websocket 路由
    app.view("/ws/chat", WebSocketView())
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
