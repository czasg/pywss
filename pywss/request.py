import struct
from pywss.encryption import Encryption


class WebSocketRequest:

    def __init__(self, sock, sockets_refs=None):
        self._sock = sock
        self._sockets_refs = sockets_refs or {}

    def shutdown(self, *args, **kwargs):
        self._sock.shutdown(*args, **kwargs)

    def close(self):
        self._sock.close()

    def recv(self, bufsize: int) -> bytes:
        return self._sock.recv(bufsize)

    def recv_first(self, bufsize: int) -> bytes:
        self.first = False
        return self.recv(bufsize)

    def _recv_safe(self, bufsize: int, response: bytes = b''):
        loop = bufsize // 4096
        remain = bufsize % 4096
        while loop:
            response += self.recv(4096)
            loop -= 1
        response += self.recv(remain)
        return response

    def ws_recv(self):
        response = self.recv(2)
        length = response[1] & 0b1111111
        if length is 0b1111110:
            response += self.recv(2)
            _, data_length = struct.unpack('!BH', response[1:4])
        elif length is 0b1111111:
            response += self.recv(8)
            _, data_length = struct.unpack('!BQ', response[1:10])
        else:
            data_length = length
        data_length += 4
        response = self._recv_safe(data_length, response)
        return Encryption.decode_msg(response)

    def ws_send(self, data):
        data = Encryption.dumps_byte(data)
        data = Encryption.encode_msg(data)
        self.write(data)

    def write(self, data):
        self._sock.sendall(data)

    def ws_send_to_all(self, data):
        for sock in self._sockets_refs.values():
            try:
                sock.ws_send(data)
            except:
                continue
