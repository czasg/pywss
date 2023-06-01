# coding: utf-8
import loggus
import pywss
import unittest

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

    def test_view(self):
        class View:
            def http_get(self, ctx: pywss.Context):
                ctx.write("test")

        app = pywss.App()
        app.view("/test", View())
        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "test")
        self.assertEqual(int(resp.headers.get("Content-Length")), 4)

    def test_view_modules(self):
        app = pywss.App()
        app.view_modules("view")

        resp = pywss.HttpTestRequest(app).get("/test-view-modules")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "test")
        self.assertEqual(int(resp.headers.get("Content-Length")), 4)

        # resp = pywss.HttpTestRequest(app).get("/test-view-modules/test")
        # self.assertEqual(resp.status_code, 200)
        # self.assertEqual(resp.body, "test")
        # self.assertEqual(int(resp.headers.get("Content-Length")), 4)

    def test_callme(self):
        def call(_):
            pass

        app = pywss.App()
        app.callme(call)


if __name__ == '__main__':
    unittest.main()
