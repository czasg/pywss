import logging

from weakref import finalize
from collections import defaultdict
from threading import current_thread

from pywss.snow_key import id_pool

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
        self.send_to_connector = send_to_connector
        self.send_to_all = send_to_all


class ConnectManager:
    connectors = defaultdict(dict)

    @classmethod
    def online(cls):
        return len(cls.connectors)

    @classmethod
    def exists(cls, name):
        return name in cls.connectors and cls.connectors[name].values()

    @classmethod
    def add_connector(cls, name, key, value):

        def remove_connectors(name=name, key=key, clear_level=value.clear_level):
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
            finally:
                logger.warning('{} Connect Close'.format(key))

        finalize(current_thread(), remove_connectors)
        cls.connectors[name][key] = value

    @classmethod
    def send_to_connector(cls, name, msg):
        try:
            for connector in cls.connectors[name].values():
                try:
                    connector.request.ws_send(msg)
                except OSError:
                    continue
            logger.info('send msg success')
            return True
        except:
            return False

    @classmethod
    def send_to_all(cls, msg):
        try:
            for connector in cls.next_user():
                try:
                    connector.request.ws_send(msg)
                except OSError:
                    continue
            logger.info('send msg success')
            return True
        except:
            return False

    @classmethod
    def next_user(cls):
        return [connector for connectors in cls.connectors.values()
                for connector in connectors.values()]


send_to_connector = ConnectManager.send_to_connector
send_to_all = ConnectManager.send_to_all
