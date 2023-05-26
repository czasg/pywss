# coding: utf-8
import json
import loggus
import socket
import pywss
import unittest
import threading
from pywss.constant import *

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

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

    def test_ctx_chunk(self):
        app = pywss.App()
        app.post("/test", lambda ctx: ctx.write_chunk("test"))

        resp = pywss.HttpTestRequest(app).post("/test")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get(HeaderTransferEncoding), "chunked")
        self.assertEqual(resp.body, "4\r\ntest\r\n0\r\n\r\n")

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


if __name__ == '__main__':
    unittest.main()
