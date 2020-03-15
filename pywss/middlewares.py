import threading
import logging
import time

from collections import deque
from collections.abc import Iterable

from pywss.public import *
from pywss.connector import Connector, ConnectManager
from pywss.public import PublicConfig

logger = logging.getLogger(__name__)


class BaseMiddleware:

    @classmethod
    def process_data(cls): ...

    @classmethod
    def process_input(cls, request, input_msg): return input_msg

    @classmethod
    def process_output(cls, request, output_msg): return output_msg


class RadioMiddleware(BaseMiddleware):

    @classmethod
    def process_data(cls): raise MiddlewareError


class DaemonMiddleware(BaseMiddleware):
    """each conn, just work once"""


class DataMiddleware(BaseMiddleware):
    """each data transform, it will works"""


class MiddlewareManager:
    radio_middleware = []
    daemon_middleware = {
        'process_input': deque(),
        'process_output': deque(),
    }
    data_middleware = {
        'process_input': deque(),
        'process_output': deque(),
    }
    daemon_middleware_count = 0
    data_middleware_count = 0

    @classmethod
    def check_base(cls, middleware):
        if isinstance(middleware, DaemonMiddleware):
            middle_type = 0
        elif isinstance(middleware, DataMiddleware):
            middle_type = 1
        elif isinstance(middleware, RadioMiddleware):
            middle_type = 2
        else:
            raise MiddlewareError
        return middle_type

    @classmethod
    def _add_middleware(cls, attr, middleware):
        getattr(cls, attr)['process_input'].append(getattr(middleware, 'process_input'))
        getattr(cls, attr)['process_output'].appendleft(getattr(middleware, 'process_output'))

    @classmethod
    def add_middleware(cls, middleware=None):
        if isinstance(middleware, type):
            middleware = middleware()
        middleware_type = cls.check_base(middleware)
        if not middleware_type:
            cls.daemon_middleware_count += 1
            cls._add_middleware('daemon_middleware', middleware)
        elif middleware_type is 1:
            cls.data_middleware_count += 1
            cls._add_middleware('data_middleware', middleware)
        elif middleware_type is 2:
            cls.radio_middleware.append(getattr(middleware, 'process_data'))

    @classmethod
    def add_middlewares(cls, middlewares=None):
        if middlewares and isinstance(middlewares, Iterable):
            for middleware in middlewares:
                cls.add_middleware(middleware)

    @classmethod
    def auto_add(cls, middle):
        if middle:
            if isinstance(middle, Iterable):
                cls.add_middlewares(middle)
            else:
                cls.add_middleware(middle)

    @classmethod
    def process(cls, request, data, func=None):
        try:
            for process_input in cls.data_middleware['process_input']:
                data = process_input(request, data)
            data = (func(request, data) if func else data) or PublicConfig.DEFAULT_REPLY
            for process_output in cls.data_middleware['process_output']:
                data = process_output(request, data)
            return data
        except MiddlewareError:
            return ERROR_FLAG

    @classmethod
    def daemon_process(cls, handler, request):
        try:
            if cls.daemon_middleware_count:
                data = request.ws_recv_safe()
                for process_input in cls.daemon_middleware['process_input']:
                    data = process_input(request, data)
                for process_output in cls.daemon_middleware['process_output']:
                    data = process_output(request, data)
                name, clear_level = data if isinstance(data, tuple) else (data, None)
                return Connector(request, handler.client_address, name=name, clear_level=clear_level)
        except:
            raise AuthenticationError

    @classmethod
    def radio_process(cls):
        t = threading.Thread(target=cls._process_radio)
        t.daemon = True
        logger.info('radio is enabled...')
        t.start()

    @classmethod
    def _process_radio(cls):
        """
        each conn, will push `RADIO_START` into `radio_queue` if the queue is empty.
        so this queue size will never exceed two.
        after push, this thread will execute radio middleware as you see.
        :return:
        """
        while True:
            command = radio_queue.get()  # if there is no conn, the radio middleware will blocking
            if command is RADIO_START and ConnectManager.online():
                while ConnectManager.online():
                    logger.info('broadcasting...')
                    for middleware_func in cls.radio_middleware:
                        data = middleware_func()
                        if not data:
                            continue
                        ConnectManager.send_to_all(data)
                    time.sleep(PublicConfig.RADIO_TIME)
                logger.info('radio pause...')


mwManager = MiddlewareManager()
