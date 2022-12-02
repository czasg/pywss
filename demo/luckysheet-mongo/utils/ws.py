# coding: utf-8
import pywss
import uuid
import threading


class WebSocketManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.pool = {}

    def register(self, ctx: pywss.Context):
        with self.lock:
            uid = f"{uuid.uuid4()}"
            self.pool[uid] = ctx
            return uid

    def delete(self, uid):
        with self.lock:
            self.pool.pop(uid, None)

    def notify(self, data, by):
        with self.lock:
            for uid, ctx in self.pool.items():  # type: pywss.Context
                if uid == by:
                    continue
                try:
                    ctx.ws_write(data)
                except:
                    self.pool.pop(uid, None)


manager = WebSocketManager()
