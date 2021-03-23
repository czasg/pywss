import asyncio
from pywss import AsyncPyws

ws = AsyncPyws(__name__)


@ws.route('/test/example/2')
def example_2(request, data):
    return "return directly"


@ws.route('/test/example/3')
async def example_3(request, data):
    await asyncio.sleep(3)
    return "return after sleep(3)"


if __name__ == '__main__':
    ws.serve_forever()

"""
ws = new WebSocket("ws://127.0.0.1:8866/test/example/2");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
ws.onopen = function() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send('hello, pywss!')  // you will get 'hello, pywss! - data from pywss'
    }
}

ws = new WebSocket("ws://127.0.0.1:8866/test/example/3");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
ws.onopen = function() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send('hello, pywss!')  // you will get 'hello, pywss! - data from pywss'
    }
}
"""
