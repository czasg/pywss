from queue import Queue

radio_queue = Queue()
RADIO_START = object()
ERROR_FLAG = object()


class PublicConfig:
    DEFAULT_REPLY = "Hello WebSocket"
    ERROR_COUNT_MAX = 10
    RADIO_TIME = 10


class AuthenticationError(Exception):
    """Cookie Auth fail"""


class WebSocketProtocolError(Exception):
    """Protocol Auth fail"""


class OutputTypeError(Exception):
    """Output error"""


class InvalidPath(Exception):
    """path error"""


class MiddlewareError(Exception):
    """middleware error"""
