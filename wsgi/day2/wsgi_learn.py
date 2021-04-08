# coding: utf-8
from wsgiref.simple_server import make_server


def application(environ, start_response):
    print(environ)
    start_response("200 by pywss", [("Content-Type", "text/html")])
    return [b"Hello, Pywss!"]


app = make_server("0.0.0.0", 8000, application)
app.serve_forever()
