import socketserver
import traceback
import weakref
import logging
from pywss.middleware import middleware_manager
from pywss.encryption import Encryption
from pywss.request import WebSocketRequest
from pywss.errors import DisconnectError
from pywss.route import Route

logger = logging.getLogger(__name__)


class MyServerTCPServer(socketserver.TCPServer):

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True,
                 ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        self.sockets_refs = weakref.WeakValueDictionary()
        super(MyServerTCPServer, self).__init__(server_address, RequestHandlerClass, bind_and_activate)

    def get_request(self):
        request, address = self.socket.accept()
        if self.ssl_context:
            request = self.ssl_context.wrap_socket(request, server_side=True)
        _sock_id = request.fileno()
        ws_request = WebSocketRequest(request)
        self.sockets_refs[_sock_id] = ws_request
        ws_request._sock_id = _sock_id
        ws_request._sockets_refs = self.sockets_refs
        return ws_request, address

    def verify_request(self, request, client_address):
        try:
            path, key = Encryption.parsing(request.recv(254 * 1024))
            if path in Route.routes:
                request.write(key)
                request.__route__ = path
                return True
        except:
            pass
        return False


class MyServerThreadingMixIn(socketserver.ThreadingMixIn):
    block_on_close = False


class SocketHandler:

    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.func = Route.get(self.request.__route__)
        try:
            self.setup()
            self.first_request()
            self.handle()
        except:
            pass
        finally:
            self.finish()

    def setup(self):
        for radio in middleware_manager.radios:
            if radio.is_empty():
                radio.put(True)
        logger.info("{} connect".format(self.client_address))

    def first_request(self):
        if middleware_manager.before_first_requests:
            data = self.request.ws_recv()
            for first_func in middleware_manager.before_first_requests:
                res = first_func(self.request, data)
                if res:
                    self.request.ws_send(res)

    def handle(self):
        while True:
            try:
                data = self.request.ws_recv()
                for func in middleware_manager.before_requests:
                    data = func(self.request, data)
                    if data:
                        break
                if not data:
                    data = self.func(self.request, data)
                if data:
                    self.request.ws_send(data)
            except TypeError:
                logger.error("transmit data error \n{}".format(traceback.format_exc()))
                continue
            except (DisconnectError, OSError):
                break
            except:
                logger.error("there exists some mistakes in pywss \n{}".format(traceback.format_exc()))
                break

    def finish(self):
        self.server.sockets_refs.pop(self.request._sock_id, None)
        logger.warning('{} disconnect!'.format(self.client_address))
