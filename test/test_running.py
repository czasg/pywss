# coding: utf-8
import time
import json
import loggus
import socket
import pywss
import unittest
import threading
from datetime import timedelta
from pywss.constant import *
import urllib.request

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

    def test_app_run(self):
        app = pywss.App()
        threading.Thread(target=lambda: time.sleep(0.5) or app.close() or pywss.Closing.close()).start()
        app.run(port=0, grace=1)
        self.assertEqual(app.running, False)

    def test_app_run2(self):
        app = pywss.App()
        threads = [
            threading.Thread(target=app.run),
            threading.Thread(target=lambda: time.sleep(0.5) or app.close() or pywss.Closing.close())
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(app.running, False)


if __name__ == '__main__':
    unittest.main()
