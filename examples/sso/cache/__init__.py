# coding: utf-8
import time
import threading

lock = threading.Lock()


class Cache:

    def __init__(self):
        self.pool = {}

    def get(self, token):
        exp = self.pool.get(token)
        if not exp:
            return
        if exp < time.time():
            lock.acquire()
            self.pool.pop(token)
            lock.release()
            return
        return exp

    def set(self, token):
        lock.acquire()
        self.pool[token] = time.time() + 1800
        lock.release()


cache = Cache()
