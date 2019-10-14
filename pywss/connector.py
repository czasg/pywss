import logging

from collections import defaultdict

from pyws.snow_key import id_pool

logger = logging.getLogger(__name__)


class Connector:
    def __init__(self, request, client_address, name=None, clear_level=None):
        self.request = request
        self.client_address = ':'.join([str(i) for i in client_address])
        if name:
            self.name = name
            self.clear_level = 0 if clear_level is None else clear_level
        else:
            self.name = str(id_pool.next_id())
            self.clear_level = 1 if clear_level is None else clear_level


class ConnectManager:
    connectors = defaultdict(dict)

    @classmethod
    def online(cls):
        return len(cls.connectors)

    @classmethod
    def clear(cls, name, key=None, clear_level=None):
        try:
            if not key:
                cls.connectors.pop(name)
            if key in cls.connectors[name]:
                if clear_level:
                    cls.connectors.pop(name)
                else:
                    cls.connectors[name].pop(key)
        except:
            pass

    @classmethod
    def add_connector(cls, name, key, value):
        cls.connectors[name][key] = value

    @classmethod
    def send_to_connector(cls, name, msg):
        try:
            for connector in cls.connectors[name].values():
                connector.request.ws_send(msg)
            logger.info('发送成功')
            return True
        except:
            return False

    @classmethod
    def send_to_all(cls, msg):
        try:
            for connector in cls.next_user():
                connector.request.ws_send(msg)
            logger.info('发送成功')
            return True
        except:
            return False

    @classmethod
    def next_user(cls):
        yield from (connector for connectors in cls.connectors.values()
                    for connector in connectors.values())
