# coding: utf-8
from pywss.ctx import Ctx
from pywss.route import RouteMap


def application(environ, start_response):
    pathParams, handlers, err = RouteMap.search(f"{environ['REQUEST_METHOD']}{environ['PATH_INFO']}")
    if err:
        start_response(err, [])
        return [b"page not found"]
    ctx = Ctx(environ, handlers, pathParams)
    ctx.next()
    start_response(f"{ctx.statusCode()} by pywss", ctx.responseHeaders())
    return ctx.responseBody()


def run(host="0.0.0.0", port=8080):
    from wsgiref.simple_server import make_server
    from pywss.wsgi.handler import WithoutLogHandler

    make_server(host, port, application, handler_class=WithoutLogHandler).serve_forever()
