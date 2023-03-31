# coding: utf-8
import time
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

    def test_cache(self):
        app = pywss.App()
        app.get("/200", pywss.NewCacheHandler(maxCache=1), lambda ctx: ctx.write([time.time()]))
        app.get("/400", pywss.NewCacheHandler(), lambda ctx: ctx.set_status_code(400) or ctx.write([time.time()]))
        app.get("/file", pywss.NewCacheHandler(), lambda ctx: ctx.write_file(__file__))

        resp = pywss.HttpTestRequest(app).get("/200").body
        time.sleep(0.01)
        self.assertEqual(resp, pywss.HttpTestRequest(app).get("/200").body)
        time.sleep(0.01)
        self.assertEqual(resp, pywss.HttpTestRequest(app).get("/200").body)
        time.sleep(0.01)
        self.assertNotEqual(resp, pywss.HttpTestRequest(app).get("/200?k=v").body)

        resp = pywss.HttpTestRequest(app).get("/400").body
        time.sleep(0.01)
        self.assertNotEqual(resp, pywss.HttpTestRequest(app).get("/400").body)
        time.sleep(0.01)
        self.assertNotEqual(resp, pywss.HttpTestRequest(app).get("/400").body)

        resp = pywss.HttpTestRequest(app).get("/file").body
        time.sleep(0.01)
        self.assertEqual(resp, pywss.HttpTestRequest(app).get("/file").body)
        time.sleep(0.01)
        self.assertEqual(resp, pywss.HttpTestRequest(app).get("/file").body)

    def test_cors(self):
        app = pywss.App()
        app.use(pywss.NewCORSHandler())
        app.options("/cors", lambda ctx: None)
        app.get("/cors", lambda ctx: ctx.write("test"))

        resp = pywss.HttpTestRequest(app).options("/cors")
        self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")
        self.assertEqual(resp.headers.get("Access-Control-Allow-Credentials"), "true")

        resp = pywss.HttpTestRequest(app).get("/cors")
        self.assertEqual(resp.body, "test")

    def test_jwt(self):
        secret = "test"

        app = pywss.App()
        app.use(pywss.NewJWTHandler(secret=secret, ignore_route=("/register",)))
        app.get("/register", lambda ctx: ctx.set_header("Authorization", ctx.data.jwt.encrypt(name="pywss")))
        app.get("/login", lambda ctx: ctx.write("ok"))

        resp = pywss.HttpTestRequest(app).get("/register")
        self.assertEqual(resp.status_code, 200)
        authorization = resp.headers.get("Authorization")
        self.assertEqual(pywss.JWT(secret).decrypt(authorization)["name"], "pywss")

        resp = pywss.HttpTestRequest(app).set_header("Authorization", authorization).get("/login")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.body, "ok")

        resp = pywss.HttpTestRequest(app). \
            set_header("Authorization", pywss.JWT(secret, expire=-1000).encrypt()). \
            get("/login")
        self.assertEqual(resp.status_code, 403)

        # ignore_startswith
        app = pywss.App()
        app.use(pywss.NewJWTHandler(secret=secret, ignore_startswith=("/register",)))
        app.get("/register", lambda ctx: ctx.set_header("Authorization", ctx.data.jwt.encrypt(name="pywss")))
        app.get("/login", lambda ctx: ctx.write("ok"))
        resp = pywss.HttpTestRequest(app).get("/register")
        self.assertEqual(resp.status_code, 200)
        authorization = resp.headers.get("Authorization")
        self.assertEqual(pywss.JWT(secret).decrypt(authorization)["name"], "pywss")

        # ignore_endswith
        app = pywss.App()
        app.use(pywss.NewJWTHandler(secret=secret, ignore_endswith=("/register",)))
        app.get("/register", lambda ctx: ctx.set_header("Authorization", ctx.data.jwt.encrypt(name="pywss")))
        app.get("/login", lambda ctx: ctx.write("ok"))
        resp = pywss.HttpTestRequest(app).get("/register")
        self.assertEqual(resp.status_code, 200)
        authorization = resp.headers.get("Authorization")
        self.assertEqual(pywss.JWT(secret).decrypt(authorization)["name"], "pywss")

        # jwt
        jwtExcept = None
        try:
            pywss.JWT(secret).decrypt("Bearer test")
        except Exception as e:
            jwtExcept = e
        self.assertIsNotNone(jwtExcept)
        # jwt
        jwtExcept = None
        try:
            jwt = pywss.JWT(secret)
            token = jwt.encrypt(name="test")
            jwt.decrypt(token + "xxx")
        except Exception as e:
            jwtExcept = e
        self.assertIsNotNone(jwtExcept)

    def test_recover(self):
        app = pywss.App()
        app.use(pywss.NewRecoverHandler(default_content={"code": 500}, traceback=True))
        app.get("/recover", lambda ctx: 1 / 0)

        resp = pywss.HttpTestRequest(app).get("/recover")
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.body, '{"code": 500}')

    def test_static(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            app = pywss.App()
            app.get("/write-buffer", lambda ctx: ctx.write(open(os.path.join(tmpdir, "pywss"), "rb")))
            app.get("/write-file-str", lambda ctx: ctx.write_file(os.path.join(tmpdir, "pywss")))
            app.static("/test", rootDir=tmpdir, staticHandler=lambda rootDir: pywss.NewStaticHandler(rootDir, limit=7))
            os.makedirs(os.path.join(tmpdir, "empty_child_dir"))
            for name in ["pywss", "test.html", "test.css", "test.js", "test.json", "test.xml", "test.png", "text.txt"]:
                tmpfile = os.path.join(tmpdir, name)
                with open(tmpfile, "w", encoding="utf-8") as f:
                    f.write("test")
                resp = pywss.HttpTestRequest(app).get(f"/test/{name}")
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.body == "test")
                self.assertTrue(int(resp.headers["Content-Length"]) == 4)

                resp = pywss.HttpTestRequest(app).head(f"/test/{name}")
                self.assertEqual(resp.status_code, 200)
                self.assertTrue(resp.body == "")
                self.assertTrue(int(resp.headers["Content-Length"]) == 4)

                resp = pywss.HttpTestRequest(app).get(f"/test/{name}/no/found")
                self.assertEqual(resp.status_code, pywss.StatusNotFound)

                resp = pywss.HttpTestRequest(app).get(f"/test/{name}", headers={"Content-Range": "0"})
                self.assertEqual(resp.status_code, pywss.StatusServiceUnavailable)

            resp = pywss.HttpTestRequest(app).get(f"/test")
            self.assertEqual(resp.status_code, 302)
            resp = pywss.HttpTestRequest(app).get(f"/test/")
            self.assertEqual(resp.status_code, 200)
            resp = pywss.HttpTestRequest(app).get(f"/write-buffer")
            self.assertEqual(resp.status_code, 200)
            resp = pywss.HttpTestRequest(app).get(f"/write-file-str")
            self.assertEqual(resp.status_code, 200)

            raiseErr = None
            try:
                app = pywss.App()
                app.static("/test", rootDir=tmpdir + "not-exist-dir")
            except Exception as e:
                raiseErr = e
            self.assertIsNotNone(raiseErr)
