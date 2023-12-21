# coding: utf-8
import loggus
import pywss
import unittest
import tempfile

loggus.SetLevel(loggus.PANIC)


class TestBase(unittest.TestCase):

    def test_basic(self):
        # json
        body = {"name": "pywss-test"}
        app = pywss.App()
        app.any("/", lambda ctx: ctx.write(ctx.json()))
        self.assertEqual(pywss.HttpTestRequest(app).post("/", json=body).json(), body)
        # form
        body = {"name": "pywss-test"}
        app = pywss.App()
        app.any("/", lambda ctx: ctx.write(ctx.form()))
        self.assertEqual(pywss.HttpTestRequest(app).post("/", data=body).json(), body)
        # file
        file1 = tempfile.NamedTemporaryFile(delete=True)
        file1.write(b"file1")
        file1.seek(0)
        file2 = tempfile.NamedTemporaryFile(delete=True)
        file2.write(b"file2")
        file2.seek(0)
        body = {
            "file1": file1,
            "file2": file2,
        }
        app = pywss.App()
        app.any("/", lambda ctx: ctx.write({k: str(v) for k, v in ctx.file().items()}))
        self.assertEqual(pywss.HttpTestRequest(app).post("/", files=body).json(), {"file1": "file1", "file2": "file2"})
        # params
        body = {"name": "pywss-test"}
        app = pywss.App()
        app.any("/", lambda ctx: ctx.write(ctx.url_params))
        self.assertEqual(pywss.HttpTestRequest(app).post("/", params=body).json(), body)
        # cookies
        body = {"name": "pywss-test"}
        app = pywss.App()
        app.any("/", lambda ctx: ctx.write(ctx.cookies))
        self.assertEqual(pywss.HttpTestRequest(app).post("/", cookies=body).json(), body)


if __name__ == '__main__':
    unittest.main()
