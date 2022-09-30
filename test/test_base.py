# coding: utf-8
import json, os
import loggus
import socket
import pywss
import unittest
import tempfile
import threading

loggus.SetLevel(loggus.PANIC)


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
                                             params={
                                                 "test:query,required": "pywss",
                                                 "page_size": "123",
                                             },
                                             request={
                                                 "dict": {"test": "swagger"},
                                                 "list": [1, 2, 3],
                                                 "list1": [[1, 2, 3]],
                                                 "list2": [],
                                                 "listObject": [{"test": "swagger"}],
                                                 "descVersion": ("1.0.0", "版本说明"),
                                                 "desclistObject": [({"test": "swagger"}, "test")],
                                             },
                                             response={"test": "swagger"})(lambda ctx: ctx.write("swagger")))
        app.get("/hello/{name}", pywss.openapi.docs(
            params={"name:path,required": "test"}
        )(lambda ctx: ctx.write({"hello": ctx.paths["name"]})))

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

    def test_run(self):
        app = pywss.App()
        app.use(lambda ctx: ctx.next())
        threading.Thread(target=lambda: app.close() or pywss.Closing.close()).start()
        app.run()

    def test_connect_err(self):
        def raiseException(ctx: pywss.Context):
            ctx.data.name = "test"
            raise Exception(ctx.data.age)

        def raiseConnectionAbortedError(ctx: pywss.Context):
            raise ConnectionAbortedError("test")

        app = pywss.App()
        app.get("/raiseException", raiseException)
        app.get("/raiseConnectionAbortedError", raiseConnectionAbortedError)

        request = pywss.HttpTestRequest(app)
        self.assertEqual(request.get("/raiseException").content, b"")
        self.assertEqual(request.get("/raiseConnectionAbortedError").content, b"")

    def test_websocket(self):
        def websocket(ctx: pywss.Context):
            err = pywss.WebSocketUpgrade(ctx)
            if err:
                ctx.log.error(err)
                ctx.set_status_code(pywss.StatusBadRequest)
                return
            self.assertEqual(ctx.ws_read(), b"test")
            ctx.ws_write(b"test")

        app = pywss.App()
        app.get("/websocket", websocket)
        app.build()
        s, c = socket.socketpair()
        threading.Thread(target=app._, args=(s, None)).start()
        c.sendall(b'GET /websocket HTTP/1.1\r\n'
                  b'Upgrade: websocket\r\n'
                  b'Host: localhost:8080\r\n'
                  b'Origin: http://localhost:8080\r\n'
                  b'Sec-WebSocket-Key: LvJ3S1F2dEnm+8GNaapAgg==\r\n'
                  b'Sec-WebSocket-Version: 13\r\n'
                  b'Connection: Upgrade\r\n\r\n')
        resp = c.recv(1024)
        self.assertIn(b"101 Switching Protocols", resp)
        self.assertIn(b"Upgrade: websocket", resp)
        self.assertIn(b"Connection: Upgrade", resp)
        self.assertIn(b"Sec-WebSocket-Accept: eVZ4hOFNJGMIfDNEG3b/VpD7CNk=", resp)
        c.sendall(b'\x81\x84\xfd\xd9\xd7\xb5\x89\xbc\xa4\xc1')
        resp = c.recv(1024)
        self.assertIn(b'test', resp)


if __name__ == '__main__':
    unittest.main()
