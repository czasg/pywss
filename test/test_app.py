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

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

    def test_app_route_register(self):
        # get
        app = pywss.App()
        app.get("/get", lambda ctx: ctx.write("get"))
        resp = pywss.HttpTestRequest(app).get("/get")
        self.assertEqual(resp.body, "get")
        app = pywss.App()
        app.get("/", lambda ctx: ctx.write("get"))
        resp = pywss.HttpTestRequest(app).get("/")
        self.assertEqual(resp.body, "get")
        app = pywss.App()
        app.get("/*", lambda ctx: ctx.write("get"))
        resp = pywss.HttpTestRequest(app).get("/123")
        self.assertEqual(resp.body, "get")
        resp = pywss.HttpTestRequest(app).get("/")
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

        # view - ins
        class ViewIns:

            def __init__(self):
                self.count = 0
                self.use = [self.add_count]

            def add_count(self, ctx: pywss.Context):
                self.count += 1
                ctx.next()

            def http_get(self, ctx: pywss.Context):
                ctx.write(f"get-view-{self.count}")

            def http_post(self, ctx: pywss.Context):
                ctx.write(f"post-view-{self.count}")

        app = pywss.App()
        app.view("/view", ViewIns())
        resp = pywss.HttpTestRequest(app).get("/view")
        self.assertEqual(resp.body, "get-view-1")
        resp = pywss.HttpTestRequest(app).post("/view")
        self.assertEqual(resp.body, "post-view-2")

        # error - register
        err = None
        try:
            app = pywss.App()
            app.get("/get")
        except Exception as e:
            err = e
        self.assertIsNotNone(err)
        # error - view
        err = None
        try:
            app = pywss.App()
            app.view("/view")
        except Exception as e:
            err = e
        self.assertIsNotNone(err)

    def test_app_body(self):
        # self.body() by Content-Length
        app = pywss.App()
        app.post("/post-body", lambda ctx: ctx.write(ctx.body()))
        resp = pywss.HttpTestRequest(app).post("/post-body", data="test")
        self.assertEqual(resp.body, "test")
        # self.body() by Transfer-Encoding
        app = pywss.App()
        app.post("/post-body", lambda ctx: ctx.write(ctx.body()))
        resp = pywss.HttpTestRequest(app).post(
            "/post-body",
            headers={
                "Content-Length": "0",
                "Transfer-Encoding": "chunked",
            },
            data="4\r\ntest\r\n5\r\n-for-\r\n5\r\npywss\r\n0\r\n\r\n",
        )
        self.assertEqual(resp.body, "test-for-pywss")
        # self.stream() by Content-Length
        app = pywss.App()
        app.post("/post-body", lambda ctx: ctx.write(b"".join(list(ctx.stream()))))
        resp = pywss.HttpTestRequest(app).post("/post-body", data="test")
        self.assertEqual(resp.body, "test")
        # self.stream() by Transfer-Encoding
        app = pywss.App()
        app.post("/post-body", lambda ctx: ctx.write(b"".join(list(ctx.stream()))))
        resp = pywss.HttpTestRequest(app).post(
            "/post-body",
            headers={
                "Content-Length": "0",
                "Transfer-Encoding": "chunked",
            },
            data="4\r\ntest\r\n5\r\n-for-\r\n5\r\npywss\r\n0\r\n\r\n",
        )
        self.assertEqual(resp.body, "test-for-pywss")

    def test_app_stream_lines(self):
        app = pywss.App()
        app.post("/post-body", lambda ctx: ctx.write(b"".join(list(ctx.stream(readline=True)))))
        resp = pywss.HttpTestRequest(app).post(
            "/post-body",
            data="4\r\ntest\r\n5\r\n-for-\r\n5\r\npywss\r\n0\r\n\r\n",
        )
        self.assertEqual(resp.body, "4\r\ntest\r\n5\r\n-for-\r\n5\r\npywss\r\n0\r\n\r\n")

    def test_app_bad_request(self):
        s, c = socket.socketpair()
        with s, c:
            app = pywss.App()
            threading.Thread(target=app.handler_request, args=(s, None)).start()
            c.sendall(b"xxx\r\n")
            respBody = c.recv(1024)
            self.assertNotIn(b"HTTP/1.1 200 OK", respBody)
            self.assertIn(b"HTTP/1.1 400 BadRequest", respBody)

        s, c = socket.socketpair()
        with s, c:
            app = pywss.App()
            threading.Thread(target=app.handler_request, args=(s, None)).start()
            c.sendall(b"GET / HTTP/1.1\r\ntest\r\n")
            respBody = c.recv(1024)
            self.assertNotIn(b"HTTP/1.1 200 OK", respBody)
            self.assertIn(b"HTTP/1.1 400 BadRequest", respBody)

    def test_app_run(self):
        app = pywss.App()
        threading.Thread(target=lambda: time.sleep(0.5) or app.close() or pywss.Closing.close()).start()
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
                "test:path": "test",
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
                "test2": [],
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
            response=["test"]
        )(lambda ctx: ctx.write("test")))

        resp = pywss.HttpTestRequest(app).get("/docs/openapi.json")
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
            "test", "test", path="/view", maxAge=timedelta(days=1)
        ))
        app.get("/expires", lambda ctx: ctx.set_cookie(
            "test", "test", path="/view", expires=10
        ))
        app.get("/secure", lambda ctx: ctx.set_cookie(
            "test", "test", secure=True
        ))

        resp = pywss.HttpTestRequest(app).get("/maxAge")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test=test", resp.headers.get("Set-Cookie"))
        self.assertIn("Expires=", resp.headers.get("Set-Cookie"))
        self.assertIn("Path=/view", resp.headers.get("Set-Cookie"))

        resp = pywss.HttpTestRequest(app).get("/expires")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test=test", resp.headers.get("Set-Cookie"))
        self.assertIn("Expires=", resp.headers.get("Set-Cookie"))
        self.assertIn("Path=/view", resp.headers.get("Set-Cookie"))

        resp = pywss.HttpTestRequest(app).get("/secure")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("test=test", resp.headers.get("Set-Cookie"))
        self.assertIn("Secure", resp.headers.get("Set-Cookie"))

    def test_ctx_redirect(self):
        app = pywss.App()
        app.get("/test", lambda ctx: ctx.redirect("/test/"))

        resp = pywss.HttpTestRequest(app).get("/test?test=test")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.headers.get("Location"), "/test/?test=test")

    def test_ctx_headers(self):
        def header(ctx: pywss.Context):
            self.assertEqual(ctx.url_params["test"], ["test", "test", "test"])
            self.assertEqual(ctx.url_params["test1"], "test")
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
        app.get("/test", lambda ctx: ctx.write("test") or ctx.next())

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

        app = pywss.App()
        app.post("/form", lambda ctx: ctx.write(ctx.form()))
        resp = pywss.HttpTestRequest(app).post("/form", headers={
            HeaderContentType: 'multipart/form-data; boundary="boundary"'
        }, data="""
--boundary
Content-Disposition: form-data; name="key1"\r\n\r\nvalue1
--boundary
Content-Disposition: form-data; name="key2"; filename="example.txt"\r\n\r\nvalue2
--boundary--""")
        self.assertEqual(json.loads(resp.body), {"key1": "value1", "key2": "value2"})

    def test_ctx_form_data(self):
        def upload(ctx: pywss.Context):
            self.assertEqual(ctx.form()["file"], "test")

        app = pywss.App()
        app.post("/upload", upload)
        app.build()
        s, c = socket.socketpair()
        with s, c:
            threading.Thread(target=app.handler_request, args=(s, None)).start()
            requestBody = b'POST /upload HTTP/1.1\r\nHost: localhost:8080\r\nUser-Agent: python-requests/2.22.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\nContent-Length: 144\r\nContent-Type: multipart/form-data; boundary=445e813923e368417a24e9a6476b3c54\r\n\r\n--445e813923e368417a24e9a6476b3c54\r\nContent-Disposition: form-data; name="file"; filename="file"\r\n\r\ntest\r\n--445e813923e368417a24e9a6476b3c54--\r\n'
            c.sendall(requestBody)
            self.assertIn(b"HTTP/1.1 200", c.recv(1024))

    def test_ctx_file(self):
        def upload(ctx: pywss.Context):
            self.assertEqual(ctx.file()["file"].name, "file")
            self.assertEqual(ctx.file()["file"].filename, "file")
            self.assertEqual(ctx.file()["file"].content, b"test")

        app = pywss.App()
        app.post("/upload", upload)
        app.build()
        s, c = socket.socketpair()
        with s, c:
            threading.Thread(target=app.handler_request, args=(s, None)).start()
            requestBody = b'POST /upload HTTP/1.1\r\nHost: localhost:8080\r\nUser-Agent: python-requests/2.22.0\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\nContent-Length: 144\r\nContent-Type: multipart/form-data; boundary=445e813923e368417a24e9a6476b3c54\r\n\r\n--445e813923e368417a24e9a6476b3c54\r\nContent-Disposition: form-data; name="file"; filename="file"\r\n\r\ntest\r\n--445e813923e368417a24e9a6476b3c54--\r\n'
            c.sendall(requestBody)
            self.assertIn(b"HTTP/1.1 200", c.recv(1024))

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
            try:
                ctx.ws_read()
            except NotImplementedError:
                pass
            try:
                ctx.ws_read()
            except NotImplementedError:
                pass

            err = pywss.WebSocketUpgrade(ctx)
            if err:
                ctx.log.error(err)
                ctx.set_status_code(pywss.StatusBadRequest)
                return
            self.assertEqual(ctx.ws_read(), b"test")
            ctx.ws_write(b'test')

            self.assertEqual(ctx.ws_read(), b"test")
            ctx.ws_write('test')

            self.assertEqual(ctx.ws_read(), b"test")
            ctx.ws_write({"test": "test"})

            self.assertEqual(ctx.ws_read(), b"t" * 1000)
            ctx.ws_write(b"t" * 1000)

            self.assertEqual(ctx.ws_read(), b"t" * 65536)
            ctx.ws_write(b't' * 65536)

        app = pywss.App()
        app.get("/websocket", websocket)
        app.build()
        s, c = socket.socketpair()
        with s, c:
            threading.Thread(target=app.handler_request, args=(s, None)).start()
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
            self.assertIn(b'test', c.recv(1024))

            c.sendall(b'\x81\x84\xfd\xd9\xd7\xb5\x89\xbc\xa4\xc1')
            self.assertIn(b'test', c.recv(1024))

            c.sendall(b'\x81\x84\xfd\xd9\xd7\xb5\x89\xbc\xa4\xc1')
            self.assertIn(b'test', c.recv(1024))

            reqBody = b'\x81\xfe\x03\xe8A\xc4\xed75\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C5\xb0\x99C'
            c.sendall(reqBody)
            self.assertIn(b't' * 1000, c.recv(1024 * 1024))

            c.sendall(b'\x81\xff\x00\x00\x00\x00\x00\x01\x00\x00\xb2\xea&\x82' + b'\xc6\x9eR\xf6' * 65536)
            self.assertIn(b't' * 65536, c.recv(1024 * 1024 * 1024))

    def test_websocket_err(self):
        def websocket(ctx: pywss.Context):
            err = pywss.WebSocketUpgrade(ctx)
            if err:
                ctx.set_status_code(pywss.StatusBadRequest)
                return
            self.assertEqual(ctx.ws_read(), b'')

        app = pywss.App()
        app.get("/websocket", websocket)
        resp = pywss.HttpTestRequest(app).get("/websocket")
        self.assertEqual(resp.status_code, pywss.StatusBadRequest)
        resp = pywss.HttpTestRequest(app).get("/websocket", headers={"Upgrade": "websocket"})
        self.assertEqual(resp.status_code, pywss.StatusBadRequest)

        app.build()
        s, c = socket.socketpair()
        with s, c:
            threading.Thread(target=app.handler_request, args=(s, None)).start()
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
            c.sendall(b'1')

    def test_headers(self):
        import pywss.headers

        s, c = socket.socketpair()
        with s, c:
            rb = s.makefile("rb", -1)
            c.sendall(b't' * 65536 + b'\r\n')
            _, _, _, err = pywss.headers.parse_request_line(rb)
            self.assertEqual(err, "uri is too long")
            c.send(b'\r\n')
            _, _, _, err = pywss.headers.parse_request_line(rb)
            self.assertEqual(err, r"bad request line b'\n'")

        s, c = socket.socketpair()
        with s, c:
            rb = s.makefile("rb", -1)
            c.sendall(b't' * 65536 + b'\r\n')
            _, err = pywss.headers.parse_headers(rb)
            self.assertEqual(err, "headers is too long")

    def test_close(self):
        app = pywss.App()
        app.get("/is_closed", lambda ctx: ctx.is_closed())
        app.get("/close", lambda ctx: ctx.close())
        app.get("/str", lambda ctx: ctx.write(str(ctx)))
        app.get("/bytes", lambda ctx: ctx.write(bytes(ctx)))
        pywss.HttpTestRequest(app).get("/is_closed")
        pywss.HttpTestRequest(app).get("/close")
        pywss.HttpTestRequest(app).get("/str")
        pywss.HttpTestRequest(app).get("/bytes")



if __name__ == '__main__':
    unittest.main()
