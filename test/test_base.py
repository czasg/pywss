# coding: utf-8
import json, os
import loggus
import socket
import pywss
import unittest
import tempfile
import threading
from datetime import timedelta

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

    def test_app_route_register(self):
        # get
        app = pywss.App()
        app.get("/get", lambda ctx: ctx.write("get"))
        resp = pywss.HttpTestRequest(app).get("/get")
        self.assertEqual(resp.body, "get")
        # post
        app = pywss.App()
        app.post("/post", lambda ctx: ctx.write("post"))
        resp = pywss.HttpTestRequest(app).post("/post")
        self.assertEqual(resp.body, "post")
        # head
        app = pywss.App()
        app.head("/head", lambda ctx: ctx.write("head"))
        resp = pywss.HttpTestRequest(app).head("/head")
        self.assertEqual(resp.body, "head")
        # put
        app = pywss.App()
        app.put("/put", lambda ctx: ctx.write("put"))
        resp = pywss.HttpTestRequest(app).put("/put")
        self.assertEqual(resp.body, "put")
        # delete
        app = pywss.App()
        app.delete("/delete", lambda ctx: ctx.write("delete"))
        resp = pywss.HttpTestRequest(app).delete("/delete")
        self.assertEqual(resp.body, "delete")
        # delete
        app = pywss.App()
        app.delete("/delete", lambda ctx: ctx.write("delete"))
        resp = pywss.HttpTestRequest(app).delete("/delete")
        self.assertEqual(resp.body, "delete")
        # patch
        app = pywss.App()
        app.patch("/patch", lambda ctx: ctx.write("patch"))
        resp = pywss.HttpTestRequest(app).patch("/patch")
        self.assertEqual(resp.body, "patch")
        # options
        app = pywss.App()
        app.options("/options", lambda ctx: ctx.write("options"))
        resp = pywss.HttpTestRequest(app).options("/options")
        self.assertEqual(resp.body, "options")
        # any
        app = pywss.App()
        app.any("/any", lambda ctx: ctx.write("any"))
        resp = pywss.HttpTestRequest(app).get("/any")
        self.assertEqual(resp.body, "any")

    def test_app_bad_request(self):
        s, c = socket.socketpair()
        with s, c:
            app = pywss.App()
            threading.Thread(target=app._, args=(s, None)).start()
            c.sendall(b"xxx\r\n")
            respBody = c.recv(1024)
            self.assertNotIn(b"HTTP/1.1 200 OK", respBody)
            self.assertIn(b"HTTP/1.1 400 BadRequest", respBody)

        s, c = socket.socketpair()
        with s, c:
            app = pywss.App()
            threading.Thread(target=app._, args=(s, None)).start()
            c.sendall(b"GET / HTTP/1.1\r\ntest\r\n")
            respBody = c.recv(1024)
            self.assertNotIn(b"HTTP/1.1 200 OK", respBody)
            self.assertIn(b"HTTP/1.1 400 BadRequest", respBody)

    def test_app_run(self):
        app = pywss.App()
        threading.Thread(target=lambda: app.close() or pywss.Closing.close()).start()
        app.run(port=0, grace=1)
        self.assertEqual(app.running, False)

    def test_app_connect_err(self):
        def raiseException(ctx: pywss.Context):
            ctx.data.test = "test"
            raise Exception(ctx.data.test)

        def raiseConnectionAbortedError(ctx: pywss.Context):
            ctx.data.test = "test"
            raise ConnectionAbortedError(ctx.data.test)

        app = pywss.App()
        app.get("/raiseException", raiseException)
        app.get("/raiseConnectionAbortedError", raiseConnectionAbortedError)

        request = pywss.HttpTestRequest(app)
        self.assertEqual(request.get("/raiseException").content, b"")
        self.assertEqual(request.get("/raiseConnectionAbortedError").content, b"")

    def test_app_openapi(self):
        app = pywss.App()
        app.openapi(title="test")
        app.get("/test/{test}", pywss.openapi.docs(
            summary="test",
            description="test",
            params={
                "test": "test",
                "test1:query": "test",
                "test2:query,required": "test",
                "test3:header": "test",
                "test4:header,required": "test",
                "test5:path": "test",
                "test6:path,required": "test",
                "test7:cookie": "test",
                "test8:cookie,required": "test",
            },
            request={
                "test": "test",
                "test1": ("test", "test"),
                "test2": ["test"],
                "test3": (["test"], "test"),
                "test4": [["test"]],
                "test5": ([["test"]], "test"),
                "test44": [{"test": "test"}],
                "test55": ([({"test": ("test", "test")}, "test")], "test"),
                "test6": {"test": ""},
                "test7": ({"test": "test"}, "test"),
                "test8": {"test": {"test": ""}},
                "test9": ({"test": ({"test": ("test", "test")}, "test")}, "test"),
                "test10": {"test": ["test"]},
                "test11": ({"test": (["test"], "test")}, "test"),
            },
            response=([], "test")
        )(lambda ctx: ctx.write("test")))

        resp = pywss.HttpTestRequest(app).get("/openapi.json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.body)["info"]["title"], "test")
        self.assertTrue("/test/{test}" in json.loads(resp.body)["paths"])

        resp = pywss.HttpTestRequest(app).get("/docs")
        self.assertEqual(resp.status_code, 200)

        resp = pywss.HttpTestRequest(app).get("/test/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "test")

    def test_app_party(self):
        app = pywss.App()
        app.get("/test", pywss.openapi.docs()(lambda ctx: ctx.write("v0")))
        api = app.party("/api")
        api.party("/v1").get("/test/{test}", lambda ctx: ctx.write("v1"))
        api.party("/v2").get("/test/{test}", pywss.openapi.docs(
            params={"test:path,required": "test"}
        )(lambda ctx: ctx.write("v2")))
        api.party("/v3").get("/test/{test}", pywss.openapi.docs()(lambda ctx: ctx.write("v3")))

        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "v0")

        resp = pywss.HttpTestRequest(app).get("/api/v1/test/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "v1")

        resp = pywss.HttpTestRequest(app).get("/api/v2/test/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "v2")

        resp = pywss.HttpTestRequest(app).get("/api/v3/test/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "v3")

    def test_ctx_cookie(self):
        app = pywss.App()
        app.get("/maxAge", lambda ctx: ctx.set_cookie(
            "test", "test", path="/test", maxAge=timedelta(days=1)
        ))
        app.get("/expires", lambda ctx: ctx.set_cookie(
            "test", "test", path="/test", expires=10
        ))
        app.get("/secure", lambda ctx: ctx.set_cookie(
            "test", "test", secure=True
        ))

        resp = pywss.HttpTestRequest(app).get("/maxAge")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test=test", resp.headers.get("Set-Cookie"))
        self.assertIn("Expires=", resp.headers.get("Set-Cookie"))
        self.assertIn("Path=/test", resp.headers.get("Set-Cookie"))

        resp = pywss.HttpTestRequest(app).get("/expires")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test=test", resp.headers.get("Set-Cookie"))
        self.assertIn("Expires=", resp.headers.get("Set-Cookie"))
        self.assertIn("Path=/test", resp.headers.get("Set-Cookie"))

        resp = pywss.HttpTestRequest(app).get("/secure")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test=test", resp.headers.get("Set-Cookie"))
        self.assertIn("Secure", resp.headers.get("Set-Cookie"))

    def test_ctx_redirect(self):
        app = pywss.App()
        app.get("/test", lambda ctx: ctx.redirect("/test"))

        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers.get("Location"), "/test")

    def test_ctx_headers(self):
        def header(ctx: pywss.Context):
            self.assertEqual(ctx.params["test"], ["test", "test", "test"])
            self.assertEqual(ctx.params["test1"], "test")
            self.assertEqual(ctx.headers["Cookie"], "test=test")
            ctx.set_cookie("test", "test")
            ctx.set_header("test", "test")

        app = pywss.App()
        app.get("/header", header)
        resp = pywss.HttpTestRequest(app).get("/header?test=test&test=test&test=test&test1=test&test&test", headers={
            "Cookie": "test=test"
        })
        self.assertEqual(resp.headers["Test"], "test")
        self.assertIn("test=test", resp.headers["Set-Cookie"])
        self.assertIn("HTTP/1.1 200", str(resp))

    def test_ctx_text(self):
        app = pywss.App()
        app.get("/test", lambda ctx: ctx.write("test"))

        resp = pywss.HttpTestRequest(app).get("/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "test")
        self.assertEqual(int(resp.headers.get("Content-Length")), 4)

        resp = pywss.HttpTestRequest(app).get("/NoFound")
        self.assertEqual(resp.status_code, 404)

    def test_ctx_json(self):
        app = pywss.App()
        app.post("/test", lambda ctx: ctx.write(ctx.json()))

        resp = pywss.HttpTestRequest(app).post("/test", json={"test": "test"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertEqual(json.loads(resp.body), {"test": "test"})

        resp = pywss.HttpTestRequest(app).get("/NoFound")
        self.assertEqual(resp.status_code, 404)

    def test_ctx_form(self):
        def form(ctx: pywss.Context):
            self.assertEqual(ctx.form(), {"test": "test"})
            ctx.write(ctx.form())

        app = pywss.App()
        app.post("/test", form)

        resp = pywss.HttpTestRequest(app).post("/test", data={"test": "test"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertEqual(json.loads(resp.body), {"test": "test"})

    def test_ctx_form_data(self):
        def upload(ctx: pywss.Context):
            self.assertEqual(ctx.form()["file"], "test")

        app = pywss.App()
        app.post("/upload", upload)
        app.build()
        s, c = socket.socketpair()
        with s, c:
            threading.Thread(target=app._, args=(s, None)).start()
            requestBody = b'POST /upload HTTP/1.1\r\nHost: localhost:8080\r\nUser-Agent: python-requests/2.22.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\nContent-Length: 144\r\nContent-Type: multipart/form-data; boundary=445e813923e368417a24e9a6476b3c54\r\n\r\n--445e813923e368417a24e9a6476b3c54\r\nContent-Disposition: form-data; name="file"; filename="file"\r\n\r\ntest\r\n--445e813923e368417a24e9a6476b3c54--\r\n'
            c.sendall(requestBody)
            self.assertIn(b"HTTP/1.1 200", c.recv(1024))

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
        app.use(lambda ctx: ctx.next())
        app.get("/auth", auth, lambda ctx: ctx.write("test"))

        resp = pywss.HttpTestRequest(app).get("/auth")
        self.assertEqual(resp.status_code, 403)

        resp = pywss.HttpTestRequest(app).get("/auth", headers={"Auth": "test"})
        self.assertEqual(resp.status_code, 200)

    def test_websocket(self):
        def websocket(ctx: pywss.Context):
            err = pywss.WebSocketUpgrade(ctx)
            if err:
                ctx.log.error(err)
                ctx.set_status_code(pywss.StatusBadRequest)
                return
            self.assertEqual(ctx.ws_read(), b"test")
            ctx.ws_write(b"test")
            self.assertEqual(ctx.ws_read(), b"test")
            ctx.ws_write("test")
            self.assertEqual(ctx.ws_read(), b"test")
            ctx.ws_write({"test": "test"})

        app = pywss.App()
        app.get("/websocket", websocket)
        app.build()
        s, c = socket.socketpair()
        with s, c:
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
            c.sendall(b'\x81\x84\xfd\xd9\xd7\xb5\x89\xbc\xa4\xc1')
            resp = c.recv(1024)
            self.assertIn(b'test', resp)
            c.sendall(b'\x81\x84\xfd\xd9\xd7\xb5\x89\xbc\xa4\xc1')
            resp = c.recv(1024)
            self.assertIn(b'test', resp)

    def test_routing(self):
        import pywss.routing
        route = pywss.routing.Route.from_route("/test/test/{test}")
        ok, res = route.match("/test")
        self.assertEqual(ok, False)
        ok, res = route.match("/test/test1/test")
        self.assertEqual(ok, False)
        ok, res = route.match("/test/test/test")
        self.assertEqual(ok, True)
        self.assertEqual(res, {"test": "test"})


if __name__ == '__main__':
    unittest.main()
