# coding: utf-8
import loggus
from wsgiref.simple_server import make_server


class Pywss:

    def run(self, host="0.0.0.0", port=8080):
        loggus.withFieldsAuto(host, port).info("server start")
        make_server(host, port, application).serve_forever()


def application(environ, start_response):
    start_response("200 ok", [("Content-Type", "text/html")])
    return [b"Hello, Pywss!"]


if __name__ == '__main__':
    app = Pywss()
    app.run()
