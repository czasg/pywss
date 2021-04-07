# coding: utf-8
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # ipv4 + tcp
sock.bind(("0.0.0.0", 8080))
sock.listen(1024)  # max connect num in monitor queue

response = """
HTTP/1.1 200 by pywss
Content-Type: text/html; charset=UTF-8
Content-Length: 13

Hello, Pywss!
""".strip().encode()

while True:
    request, address = sock.accept()
    print(request.recv(1024 * 1024))
    request.sendall(response)
