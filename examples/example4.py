import json

from pywss import Pyws, route, DataMiddleware


class DataProcessMiddleware(DataMiddleware):
    """
    每一次数据传进来时都会进行处理
    可以用作对常见数据进行处理
    """

    @classmethod
    def process_input(cls, request, input_msg):
        return json.loads(input_msg)


@route('/test/example/4')
def example_4(request, data):
    print(type(data))


if __name__ == '__main__':
    ws = Pyws(__name__, port=8866)
    ws.add_middleware(DataProcessMiddleware)
    ws.serve_forever()

"""
/* Client Code */
ws = new WebSocket("ws://127.0.0.1:8866/test/example/4");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
ws.onopen = function() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({'name': 'example4'}))
    }
}
"""
