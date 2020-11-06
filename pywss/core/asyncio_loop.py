# coding: utf-8
import loggus
import asyncio

from pywss.encryption import Encryption
from pywss.route import Route
from pywss.request import WebSocketRequest
from pywss.middleware import middleware_manager
from pywss.errors import DisconnectError, RouteMissError
from asyncio.selector_events import _SelectorSocketTransport
from asyncio.selector_events import BaseSelectorEventLoop


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
                if transport is self: continue
                transport.ws_send(data)
            except:
                continue

    def ws_send_by_fileno(self, data, fileno=None):
        try:
            self._loop._transports.get(fileno).ws_send(data)
        except:
            pass


class WebSocketLoop(BaseSelectorEventLoop):
    def __init__(self, selector=None):
        super(WebSocketLoop, self).__init__(selector)

    def _make_socket_transport(self, sock, protocol, waiter=None, *,
                               extra=None, server=None):
        return WebSocketTransport(self, sock, protocol, waiter,
                                  extra, server)


class WebSocketProtocol(asyncio.Protocol):

    def connection_made(self, transport: WebSocketTransport):
        self.first_request = True if middleware_manager.before_first_requests else False
        self.transport = transport
        loggus.WithField("address", transport.get_extra_info('peername')).Info("connect")

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
            for func in middleware_manager.before_requests:
                res = func(self.transport, data)
                if res:
                    return self._send_result(res)
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
        for last_func in middleware_manager.after_last_requests:
            try:
                res = last_func(self.transport)
                if res and asyncio.coroutines.iscoroutine(res):
                    self.transport._loop.create_task(res)
            except Exception as e:
                loggus.WithException(e).error("connect error!")
                break
        self.transport._loop._transports.pop(self.transport._sock_fd, None)
        loggus.WithField("address", self.transport.get_extra_info("peername")).Warning("disconnect!")
