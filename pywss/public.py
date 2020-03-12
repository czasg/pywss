import json
from datetime import datetime, date
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


class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return super().default(obj)
