import re
import struct
import base64
import hashlib

from pyws.public import WebSocketProtocolError

MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
REGEX = re.compile(r'GET\s+([^\s]+).*Sec-WebSocket-Key:\s*(.*?)\r\n', re.S)
RESPONSE_TEMPLATE = "HTTP/1.1 101 Switching Protocols\r\n" \
                    "Upgrade:websocket\r\n" \
                    "Connection: Upgrade\r\n" \
                    "Sec-WebSocket-Accept: %s\r\n\r\n"


class WebSocketProtocol:

    @classmethod
    def check_header(cls, headers):
        try:
            path, key = REGEX.search(headers).groups()
            if all((path, key)):
                return path, key
        except:
            pass
        raise WebSocketProtocolError

    @classmethod
    def get_ac_str(cls, data):
        path, value = cls.check_header(str(data, encoding="utf-8"))
        return path, base64.b64encode(hashlib.sha1((value + MAGIC_STRING).encode('utf-8')).digest()).decode('utf-8')

    @classmethod
    def parsing(cls, data):
        path, key = cls.get_ac_str(data)
        return path, bytes(RESPONSE_TEMPLATE % key, encoding='utf-8')

    @classmethod
    def decode_msg(cls, data):
        payload_len = data[1] & 0b1111111
        if payload_len is 0b1111110:
            mask = data[4:8]
            decoded = data[8:]
        elif payload_len is 0b1111111:
            mask = data[10:14]
            decoded = data[14:]
        else:
            mask = data[2:6]
            decoded = data[6:]
        return str(bytearray([decoded[i] ^ mask[i % 4] for i in range(len(decoded))]), encoding='utf-8')

    @classmethod
    def encode_msg(cls, msg_bytes, token=b"\x81"):
        length = len(msg_bytes)
        if length <= 125:
            token += struct.pack("B", length)
        elif length <= 65535:
            token += struct.pack("!BH", 126, length)
        else:
            token += struct.pack("!BQ", 127, length)
        return token + msg_bytes
