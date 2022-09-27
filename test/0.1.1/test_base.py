# coding: utf-8
import json
import loggus
import pywss
import unittest

loggus.SetLevel(loggus.ERROR)


class TestBase(unittest.TestCase):

    def test_text(self):
        app = pywss.App()
        app.get("/text", lambda ctx: ctx.write("test"))

        resp = pywss.HttpTestRequest(app).get("/text")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "test")
        self.assertEqual(int(resp.headers.get("Content-Length")), 4)

        resp = pywss.HttpTestRequest(app).get("/NoFound")
        self.assertEqual(resp.status_code, 404)

    def test_json(self):
        app = pywss.App()
        app.get("/json", lambda ctx: ctx.write_json({"test": "test"}))

        resp = pywss.HttpTestRequest(app).get("/json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertEqual(json.loads(resp.body), {"test": "test"})

    def test_redirect(self):
        app = pywss.App()
        app.get("/test", lambda ctx: ctx.redirect("/test"))

        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers.get("Location"), "/test")

    def test_set_cookie(self):
        app = pywss.App()
        app.get("/test", lambda ctx: ctx.set_cookie("test", "test", path="/test"))

        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Set-Cookie"), "test=test; Path=/test")

    def test_static(self):
        app = pywss.App()
        app.static("/test", ".")

        resp = pywss.HttpTestRequest(app).get(f"/test/{__name__}.py")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("test_static" in resp.body)
        self.assertTrue(int(resp.headers.get("Content-Length")) > 0)

        resp = pywss.HttpTestRequest(app).head(f"/test/{__name__}.py")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.body == "")
        self.assertTrue(int(resp.headers.get("Content-Length")) > 0)

    def test_middleware(self):
        def auth(ctx: pywss.Context):
            password = ctx.headers.get("Auth", None)
            if password != "test":
                ctx.set_status_code(pywss.StatusForbidden)
                return
            ctx.next()

        app = pywss.App()
        app.get("/auth", auth, lambda ctx: ctx.write("test"))

        resp = pywss.HttpTestRequest(app).get("/auth")
        self.assertEqual(resp.status_code, 403)

        resp = pywss.HttpTestRequest(app).get("/auth", headers={"Auth": "test"})
        self.assertEqual(resp.status_code, 200)

    def test_party(self):
        app = pywss.App()
        api = app.party("/api")
        v1 = api.party("/v1")
        v2 = api.party("/v2")
        v1.get("/test", lambda ctx: ctx.write("v1"))
        v2.get("/test", lambda ctx: ctx.write("v2"))

        resp = pywss.HttpTestRequest(app).get("/api/v1/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "v1")

        resp = pywss.HttpTestRequest(app).get("/api/v2/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "v2")

    def test_swagger(self):
        app = pywss.App()
        app.openapi(title="test")
        app.get("/hello/{name}", pywss.openapi.docs()(lambda ctx: ctx.write({"hello": ctx.paths["name"]})))

        resp = pywss.HttpTestRequest(app).get("/openapi.json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.body)["info"]["title"], "test")
        self.assertTrue("/hello/{name}" in json.loads(resp.body)["paths"])

        resp = pywss.HttpTestRequest(app).get("/hello/world")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.body), {"hello": "world"})


if __name__ == '__main__':
    unittest.main()
