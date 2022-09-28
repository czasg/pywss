# coding: utf-8
import json, os
import loggus
import pywss
import unittest
import tempfile

loggus.SetLevel(loggus.ERROR)


class TestBase(unittest.TestCase):

    def test_methods(self):
        app = pywss.App()
        # get
        app.get("/get", lambda ctx: ctx.write("get"))
        resp = pywss.HttpTestRequest(app).get("/get")
        self.assertEqual(resp.body, "get")
        # post
        app.post("/post", lambda ctx: ctx.write("post"))
        resp = pywss.HttpTestRequest(app).post("/post")
        self.assertEqual(resp.body, "post")
        # head
        app.head("/head", lambda ctx: ctx.write("head"))
        resp = pywss.HttpTestRequest(app).head("/head")
        self.assertEqual(resp.body, "head")
        # put
        app.put("/put", lambda ctx: ctx.write("put"))
        resp = pywss.HttpTestRequest(app).put("/put")
        self.assertEqual(resp.body, "put")
        # delete
        app.delete("/delete", lambda ctx: ctx.write("delete"))
        resp = pywss.HttpTestRequest(app).delete("/delete")
        self.assertEqual(resp.body, "delete")
        # delete
        app.delete("/delete", lambda ctx: ctx.write("delete"))
        resp = pywss.HttpTestRequest(app).delete("/delete")
        self.assertEqual(resp.body, "delete")
        # patch
        app.patch("/patch", lambda ctx: ctx.write("patch"))
        resp = pywss.HttpTestRequest(app).patch("/patch")
        self.assertEqual(resp.body, "patch")
        # options
        app.options("/options", lambda ctx: ctx.write("options"))
        resp = pywss.HttpTestRequest(app).options("/options")
        self.assertEqual(resp.body, "options")
        # any
        app.any("/any", lambda ctx: ctx.write("any"))
        resp = pywss.HttpTestRequest(app).get("/any")
        self.assertEqual(resp.body, "any")

    def test_headers(self):
        app = pywss.App()
        # get
        app.get("/get", lambda ctx: ctx.write("get"))
        resp = pywss.HttpTestRequest(app).get("/get?name=pywss&name=test&name=ha&age=123", headers={
            "Cookie": "name=test"
        })
        self.assertEqual(resp.body, "get")
        app.close()

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
        app.post("/json", lambda ctx: ctx.write(ctx.json()))

        resp = pywss.HttpTestRequest(app).post("/json", json={"test": "json"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertEqual(json.loads(resp.body), {"test": "json"})

    def test_form(self):
        app = pywss.App()
        app.post("/form", lambda ctx: ctx.write(ctx.form()))

        resp = pywss.HttpTestRequest(app).post("/form", data={"test": "form"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertEqual(json.loads(resp.body), {"test": "form"})

    def test_redirect(self):
        app = pywss.App()
        app.get("/test", lambda ctx: ctx.redirect("/test"))

        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers.get("Location"), "/test")

    def test_set_cookie(self):
        app = pywss.App()
        app.get("/test", lambda ctx: ctx.set_cookie("test", "test", path="/test", expires=10))

        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test=test", resp.headers.get("Set-Cookie"))
        self.assertIn("Expires=", resp.headers.get("Set-Cookie"))
        self.assertIn("Path=/test", resp.headers.get("Set-Cookie"))

    def test_static(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app = pywss.App()
            app.static("/test", tmpdir)

            for name in ["pywss", "test.html", "test.css", "test.js", "test.json", "test.xml", "test.png"]:
                tmpfile = os.path.join(tmpdir, name)
                with open(tmpfile, "w", encoding="utf-8") as f:
                    f.write("test")
                resp = pywss.HttpTestRequest(app).get(f"/test/{name}")
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.body == "test")
                self.assertTrue(int(resp.headers["Content-Length"]) == 4)

                resp = pywss.HttpTestRequest(app).head(f"/test/pywss")
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.body == "")
                self.assertTrue(int(resp.headers["Content-Length"]) == 4)

                resp = pywss.HttpTestRequest(app).get(f"/test/{name}/no/found")
                self.assertEqual(resp.status_code, pywss.StatusNotFound)

                resp = pywss.HttpTestRequest(app).get(f"/test/{name}", headers={"Content-Range": "0"})
                self.assertEqual(resp.status_code, pywss.StatusServiceUnavailable)

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
        app.get("/hello", pywss.openapi.docs(summary="test", description="test",
                                             params={"test:query,required": "pywss"},
                                             request={"dict": {"test": "swagger"},
                                                      "list": [1, 2, 3],
                                                      "list1": [{"test": "swagger"}]},
                                             response={"test": "swagger"})(lambda ctx: ctx.write("swagger")))
        app.get("/hello/{name}", pywss.openapi.docs()(lambda ctx: ctx.write({"hello": ctx.paths["name"]})))

        resp = pywss.HttpTestRequest(app).get("/openapi.json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.body)["info"]["title"], "test")
        self.assertTrue("/hello/{name}" in json.loads(resp.body)["paths"])

        resp = pywss.HttpTestRequest(app).get("/docs")
        self.assertEqual(resp.status_code, 200)

        resp = pywss.HttpTestRequest(app).get("/hello")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "swagger")

        resp = pywss.HttpTestRequest(app).get("/hello/world")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.body), {"hello": "world"})


if __name__ == '__main__':
    unittest.main()
