from queue import Queue

radio_queue = Queue()
RADIO_START = object()
ERROR_FLAG = object()


class PublicConfig:
    DEFAULT_REPLY = "Hello WebSocket"
    ERROR_COUNT_MAX = 10
    RADIO_TIME = 10


class AuthenticationError(Exception):
    """Cookie认证失败"""


class WebSocketProtocolError(Exception):
    """协议认证失败"""


class OutputTypeError(Exception):
    """输出类型错误"""


class InvalidPath(Exception):
    """路径错误"""


class MiddlewareError(Exception):
    """中间件错误"""
