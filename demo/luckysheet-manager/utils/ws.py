# coding: utf-8
import pywss
import uuid
import threading

from collections import defaultdict


class WebSocketManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.pool = defaultdict(dict)

    def register(self, ctx: pywss.Context, excel_id):
        with self.lock:
            uid = f"{uuid.uuid4()}"
            self.pool[excel_id][uid] = ctx
            return uid

    def delete(self, uid, excel_id):
        with self.lock:
            self.pool[excel_id].pop(uid, None)

    def notify(self, data, by, excel_id):
        with self.lock:
            for uid, ctx in self.pool[excel_id].items():  # type: pywss.Context
                if uid == by:
                    continue
                try:
                    ctx.ws_write(data)
                except:
                    self.pool.pop(uid, None)


manager = WebSocketManager()
