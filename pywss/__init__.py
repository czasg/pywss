# coding: utf-8
__author__ = 'CzaOrz <https://github.com/CzaOrz>'

import ssl
import loggus
import asyncio
from pywss.route import Route, route
from pywss.middleware import RadioMiddleware, AsyncRadioMiddleware

from pywss.core.asyncio_loop import WebSocketProtocol, WebSocketLoop
from pywss.core.threading_handler import MyServerThreadingMixIn, MyServerTCPServer, SocketHandler
from pywss.middleware import middleware_manager


def load_ssl_context(pem, key, version=None):
    ssl_context = ssl.SSLContext(version or ssl.PROTOCOL_TLSv1)
    ssl_context.load_cert_chain(pem, key)
    return ssl_context


class Server:
    def __init__(self, routes_module, address='0.0.0.0', port=8866,
                 logging_level=loggus.INFO):
        loggus.SetLevel(logging_level)
        loggus.info('Server Start ...')
        loggus.info('Server Address is %s:%d' % (address, port))
        self.address = address
        self.port = port
        self.middleware_manager = middleware_manager
        self.add_routes(routes_module)

    def add_middleware(self, middleware):
        self.middleware_manager.add_middleware(middleware)

    def add_routes(self, module):
        Route.add_routes(module)

    @staticmethod
    def route(path):
        def wrapper(func):
            Route.add_route(path, func)
            return func

        return wrapper

    @staticmethod
    def before_first_request(func):
        middleware_manager.add_before_first_request(func)

    @staticmethod
    def before_request(func):
        middleware_manager.add_before_request(func)

    def serve_forever(self, poll_interval=0.5):
        raise NotImplementedError


class Pyws(MyServerThreadingMixIn, MyServerTCPServer, Server):

    def __init__(self, routes_module,
                 address='0.0.0.0', port=8866,
                 RequestHandlerClass=SocketHandler,
                 logging_level=loggus.INFO, **kwargs):
        Server.__init__(self, routes_module, address, port, logging_level)
        MyServerTCPServer.__init__(self, (address, port), RequestHandlerClass, **kwargs)

    def add_middleware(self, middleware_cls):
        middleware = middleware_cls.from_transports(self.sockets_refs)
        super(Pyws, self).add_middleware(middleware)

    def serve_forever(self, poll_interval=0.5):
        self.middleware_manager.run()
        super(Pyws, self).serve_forever(poll_interval)


class Pywss(Pyws):

    def __init__(self, routes_module, ssl_pem=None, ssl_key=None, ssl_context=None, ssl_version=None, **kwargs):
        if ssl_context:
            pass
        elif ssl_pem and ssl_key:
            ssl_context = load_ssl_context(ssl_pem, ssl_key, ssl_version)
        else:
            raise Exception("you should define ssl file path")
        super(Pywss, self).__init__(routes_module, ssl_context=ssl_context, **kwargs)


class AsyncPyws(Server):
    def __init__(self, routes_module, address='0.0.0.0', port=8866,
                 logging_level=loggus.INFO):
        super(AsyncPyws, self).__init__(routes_module, address, port, logging_level)
        asyncio.set_event_loop(WebSocketLoop())
        self.loop = asyncio.get_event_loop()

    def add_middleware(self, middleware_cls):
        middleware = middleware_cls.from_transports(self.loop._transports)
        super(AsyncPyws, self).add_middleware(middleware)

    @staticmethod
    def after_last_request(func):
        middleware_manager.add_after_last_request(func)

    async def _server_forever(self):
        server = await self.loop.create_server(lambda: WebSocketProtocol(), self.address, self.port)
        async with server:
            await server.serve_forever()

    def serve_forever(self, *args):  # todo, add os.fork() to run in multiprocessing
        self.middleware_manager.run()
        self.loop.create_task(self._server_forever())
        self.loop.run_forever()


class AsyncPywss(AsyncPyws):
    """todo, add support"""
