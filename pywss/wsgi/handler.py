# coding: utf-8
from wsgiref.simple_server import WSGIRequestHandler


class WithLogHandler(WSGIRequestHandler):

    def log_error(self, *args, **kwargs) -> None:
        pass

    def log_message(self, *args, **kwargs) -> None:
        pass

    def log_request(self, *args, **kwargs) -> None:
        pass
