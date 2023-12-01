# coding: utf-8
import os
import time
import inspect
import loggus
import pywss
import unittest
import threading

loggus.SetLevel(loggus.PANIC)


def handler(ctx):
    pass


class View:

    def http_get(self, ctx):
        pass


class TestBase(unittest.TestCase):

    def test_watch(self):
        app = pywss.App()
        app.get("/handler", handler)
        app.view("/view", View)
        app.build()
        t = threading.Thread(target=app.watchdog, args=(0.1,))
        t.start()
        time.sleep(0.3)
        module = inspect.getmodule(handler)
        sourcefile = inspect.getsourcefile(module)
        current_time = time.time()
        os.utime(sourcefile, times=(current_time, current_time))
        time.sleep(0.7)
        app.close()
        t.join()


if __name__ == '__main__':
    unittest.main()
