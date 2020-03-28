import asyncio
import queue
import time
import threading

from typing import Dict, Any, List


class MiddlewareProtocol:

    def process_data(self):
        raise NotImplementedError


class RadioMiddleware(MiddlewareProtocol):
    RADIO_TIME = 2

    def __init__(self, sockets: Dict[int, Any]):
        self.sockets = sockets
        self.queue = queue.Queue()

    @classmethod
    def from_transports(cls, transports):
        return cls(transports)

    def exists_conn(self):
        return len(self.sockets) != 0

    def is_empty(self):
        return self.queue.qsize() == 0

    def put(self, data=None):
        self.queue.put(data or True)

    def _run(self):
        while True:
            self.queue.get()  # wait until queue is not empty
            while self.exists_conn():
                data = self.process_data()
                for transport in self.sockets.values():
                    try:
                        transport.ws_send(data)
                    except:
                        continue
                time.sleep(self.RADIO_TIME)

    def run(self):
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()


class AsyncRadioMiddleware(RadioMiddleware):
    def __init__(self, transports: Dict[int, Any]):
        super(AsyncRadioMiddleware, self).__init__(transports)
        self.queue = asyncio.Queue()

    def put(self, data=None):
        self.queue.put_nowait(data or True)

    async def _run(self):
        while True:
            await self.queue.get()  # wait until queue is not empty
            while self.exists_conn():
                data = self.process_data()
                if asyncio.iscoroutine(data):
                    data = await data
                for transport in self.sockets.values():
                    try:
                        transport.ws_send(data)
                    except:
                        continue
                await asyncio.sleep(self.RADIO_TIME)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._run())


class MiddlewareManager:

    def __init__(self):
        self.radios = []  # type: List[RadioMiddleware]
        self.before_first_requests = []

    def add_middleware(self, middleware):
        if isinstance(middleware, RadioMiddleware):
            self.radios.append(middleware)

    def add_before_first_request(self, func):
        self.before_first_requests.append(func)

    def run(self):
        for radio in self.radios:
            radio.run()


middleware_manager = MiddlewareManager()
