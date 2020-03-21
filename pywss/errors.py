# coding: utf-8

class EncryptionError(Exception):
    """websocket解密异常"""


class DisconnectError(Exception):
    """断开连接"""


class RouteMissError(Exception):
    """路径异常"""


class DataFormatError(Exception):
    """数据格式异常"""
