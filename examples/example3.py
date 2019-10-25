import json

from pywss import Pyws, route, DaemonMiddleware, AuthenticationError


class AuthenticationMiddleware(DaemonMiddleware):
    """
    该中间件仅一次起作用，可以用于首次连接时的验证
    返回值有两种类型:
    第一种: string，用于作为连接者的名字
    第二种: tuple，第二参数用于指定用户退出时的清除级别
    """

    @classmethod
    def process_input(self, request, input_msg):
        json_data = json.loads(input_msg)
        if 'name' in json_data:
            return str(json_data['name']), 1
        raise AuthenticationError


@route('/test/example/3')
def example_3(request, data):
    """There Nothing To Do"""


if __name__ == '__main__':
    ws = Pyws(__name__, address='127.0.0.1', port=8866)
    ws.add_middleware(AuthenticationMiddleware)
    ws.serve_forever()

"""
/* Client Code */
ws = new WebSocket("ws://127.0.0.1:8866/test/example/3");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
ws.onopen = function() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({'name': 'example3'}))  // you will get enter the AuthenticationMiddleware first
    }
}
"""
