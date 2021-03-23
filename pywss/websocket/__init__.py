# coding: utf-8
import struct
import base64
import hashlib

MAGIC_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
RESPONSE_TEMPLATE = "HTTP/1.1 101 Switching Protocols\r\n" \
                    "Upgrade: websocket\r\n" \
                    "Connection: Upgrade\r\n" \
                    "Sec-WebSocket-Accept: %s\r\n\r\n"


def createWebSocketResponse(secKey):
    secKey = secKey + MAGIC_STRING
    secKey = hashlib.sha1((secKey).encode('utf-8')).digest()
    secKey = base64.b64encode(secKey).decode('utf-8')
    return bytes(RESPONSE_TEMPLATE % secKey, encoding='utf-8')


def websocketRecv(sock) -> bytes:
    response = sock.recv(2)
    length = response[1] & 0b1111111
    if length is 0b1111110:
        response += sock.recv(2)
        _, data_length = struct.unpack('!BH', response[1:4])
    elif length is 0b1111111:
        response += sock.recv(8)
        _, data_length = struct.unpack('!BQ', response[1:10])
    else:
        data_length = length
    data_length += 4
    loop = data_length // 4096
    remain = data_length % 4096
    while loop:
        response += sock.recv(4096)
        loop -= 1
    response += sock.recv(remain)
    return decodeMsg(response)


def decodeMsg(data) -> bytes:
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


def encodeMsg(msg_bytes, token=b"\x81") -> bytes:
    length = len(msg_bytes)
    if length <= 125:
        token += struct.pack("B", length)
    elif length <= 65535:
        token += struct.pack("!BH", 126, length)
    else:
        token += struct.pack("!BQ", 127, length)
    return token + msg_bytes
