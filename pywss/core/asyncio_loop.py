import asyncio
import logging
from pywss.encryption import Encryption
from pywss.route import Route
from pywss.request import WebSocketRequest
from pywss.middleware import middleware_manager
from pywss.errors import DisconnectError, RouteMissError
from asyncio.selector_events import _SelectorSocketTransport
from asyncio.selector_events import BaseSelectorEventLoop

logger = logging.getLogger(__name__)


class WebSocketTransport(_SelectorSocketTransport, WebSocketRequest):
    def __init__(self, loop, sock, protocol, waiter=None, extra=None, server=None):
        self.first = True
        self.func = None
        super(WebSocketTransport, self).__init__(loop, sock, protocol, waiter, extra, server)

    def _read_ready__data_received(self):
        if self._conn_lost:
            return
        try:
            data = self.recv(self.max_size) if self.first else self.ws_recv()
        except (BlockingIOError, InterruptedError):
            return
        except DisconnectError:
            return self._force_close("Test By Cza")
        except Exception as exc:
            self._fatal_error(exc, 'Fatal read error on socket transport')
            return

        if not data:
            self._read_ready__on_eof()
            return

        if self.first:
            try:
                path, key = Encryption.parsing(data)
                self.func = Route.get(path)
                self.write(key)
                self.first = False
            except RouteMissError as exc:
                self._fatal_error(exc, 'Fatal error: RouteMissError')
            return

        try:
            self._protocol.data_received(data)
        except Exception as exc:
            self._fatal_error(
                exc, 'Fatal error: protocol.data_received() call failed.')

    def ws_send_to_all(self, data):
        for transport in self._loop._transports.values():
            try:
                transport.ws_send(data)
            except:
                continue


class WebSocketLoop(BaseSelectorEventLoop):
    def _make_socket_transport(self, sock, protocol, waiter=None, *,
                               extra=None, server=None):
        return WebSocketTransport(self, sock, protocol, waiter,
                                  extra, server)


class WebSocketProtocol(asyncio.Protocol):

    def connection_made(self, transport: WebSocketTransport):
        self.first_request = True if middleware_manager.before_first_requests else False
        self.transport = transport
        logger.info(f"{transport.get_extra_info('peername')} connect")

    def data_received(self, data):
        for radio in middleware_manager.radios:
            if radio.is_empty():
                radio.put(True)

        if self.first_request:
            for first_func in middleware_manager.before_first_requests:
                res = first_func(self.transport, data)
                self._send_result(res)
            self.first_request = False
        else:
            res = self.transport.func(self.transport, data)
            self._send_result(res)

    def _send_result(self, res):
        if asyncio.coroutines.iscoroutine(res):
            def task_cb(future):
                self.transport.ws_send(future.result() or "hello Pywss")

            task = self.transport._loop.create_task(res)  # type: asyncio.tasks.Task
            task.add_done_callback(task_cb)
        elif res:
            self.transport.ws_send(res)

    def connection_lost(self, exc):
        self.transport._loop._transports.pop(self.transport._sock_fd, None)
        logger.warning(f'{self.transport.get_extra_info("peername")} disconnect!')
