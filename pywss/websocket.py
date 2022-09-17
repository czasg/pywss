# coding: utf-8
import json
import struct
import base64
import hashlib

MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
RESPONSE_TEMPLATE = "HTTP/1.1 101 Switching Protocols\r\n" \
                    "Upgrade: websocket\r\n" \
                    "Connection: Upgrade\r\n" \
                    "Sec-WebSocket-Accept: %s\r\n\r\n"


def WebSocketContextWrap(ctx):
    if ctx.headers.get("Upgrade") != "websocket":
        return "invalid websocket request"
    secKey = ctx.headers.get("Sec-WebSocket-Key")
    if not secKey:
        return "invalid websocket key"
    secResp = _createWebSocketResponse(secKey)
    ctx.fd.sendall(secResp)

    def ws_write(body):
        if isinstance(body, bytes):
            ctx.fd.sendall(_websocketEncodeMsg(body))
        elif isinstance(body, str):
            ctx.fd.sendall(_websocketEncodeMsg(body.encode("utf-8")))
        elif isinstance(body, (dict, list)):
            ctx.fd.sendall(_websocketEncodeMsg(json.dumps(body, ensure_ascii=False).encode("utf-8")))

    ctx.ws_read = lambda: _websocketRead(ctx.rfd)
    ctx.ws_write = ws_write
    return None


def _createWebSocketResponse(secKey):
    secKey = secKey + MAGIC_STRING
    secKey = hashlib.sha1((secKey).encode('utf-8')).digest()
    secKey = base64.b64encode(secKey).decode('utf-8')
    return bytes(RESPONSE_TEMPLATE % secKey, encoding='utf-8')


def _websocketRead(sock) -> bytes:
    response = sock.read(2)
    if len(response) != 2:
        return b""
    length = response[1] & 0b1111111
    if length is 0b1111110:
        response += sock.read(2)
        _, data_length = struct.unpack('!BH', response[1:4])
    elif length is 0b1111111:
        response += sock.read(8)
        _, data_length = struct.unpack('!BQ', response[1:10])
    else:
        data_length = length
    data_length += 4
    loop = data_length // 4096
    remain = data_length % 4096
    while loop:
        response += sock.read(4096)
        loop -= 1
    response += sock.read(remain)
    return _websocketDecodeMsg(response)


def _websocketDecodeMsg(data) -> bytes:
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
    return bytes(bytearray([decoded[i] ^ mask[i % 4] for i in range(len(decoded))]))


def _websocketEncodeMsg(msg_bytes, token=b"\x81") -> bytes:
    length = len(msg_bytes)
    if length <= 125:
        token += struct.pack("B", length)
    elif length <= 65535:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    return token + msg_bytes
