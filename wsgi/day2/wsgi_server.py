# coding: utf-8
import time
import loggus  # pip install loggus
import socket
import threading

from typing import List, Tuple, Callable


def parse2wsgi(sock: socket.socket) -> tuple:
    bodyStr = sock.recv(1024 * 1024).decode()

    environ = {
        "method": "",
        "path": "",
        "body": "",
        "httpVersion": "",
        "headers": {},
    }

    def start_response(status_msg: str, response_headers: List[Tuple[str, str]]) -> None:
        response = f"HTTP/1.1 {status_msg}"
        for key, value in response_headers:
            response += f"\r\n{key}: {value}"
        sock.send(f"{response}\r\n\r\n".encode())

    request_info = bodyStr.split("\r\n")
    request_row = request_info[0]
    request_header = request_info[1:-2]
    request_body = request_info[-1]

    environ["method"], environ["path"], environ["httpVersion"] = request_row.split()
    for headers in request_header:
        key, value = headers.split(":", 1)
        environ["headers"][key] = value
    environ["body"] = request_body

    return environ, start_response


class WorkerHandler:

    def __init__(self, request: socket.socket, application: Callable):
        environ, start_response = parse2wsgi(request)
        body: List[bytes] = application(environ, start_response)
        request.send(b"".join(body))
        request.close()


class Server:

    def __init__(self, host: str = "0.0.0.0", port: int = 8080, max_conn: int = 100):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4 + tcp
        sock.bind((host, port))
        sock.listen(max_conn)  # max connect num in monitor queue
        self.sock = sock
        loggus.info("serve start...")

    def serve_forever(self):
        while True:
            request, address = self.sock.accept()
            loggus.withFields({
                "ip": address[0],
                "time": int(time.time()),
            }).info("request start")
            threading.Thread(target=WorkerHandler, args=(request, application)).start()


def application(environ, start_response) -> List[bytes]:
    loggus.withFields(environ).info("environ")
    start_response("200 ok", [("Content-Type", "text/html")])
    return [b"Hello, Pywss!"]


if __name__ == '__main__':
    with loggus.withTraceback():
        Server().serve_forever()
