# coding: utf-8
import time
import os
import loggus
import pywss
import unittest
import tempfile

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

    def test_header(self):
        def handler(ctx: pywss.Context):
            ctx.set_header("x-TOKEN", "x-token")
            ctx.set_header("x-api-key", "x-api-key")
            ctx.set_header("PywssVersion", "pywss")

        app = pywss.App()
        app.get("/test", handler)

        headers = pywss.HttpTestRequest(app).get("/test").headers
        self.assertIn("X-Token", headers)
        self.assertNotIn("x-TOKEN", headers)
        self.assertIn("X-Api-Key", headers)
        self.assertNotIn("x-api-key", headers)
        self.assertIn("Pywssversion", headers)
        self.assertNotIn("PywssVersion", headers)


if __name__ == '__main__':
    unittest.main()
