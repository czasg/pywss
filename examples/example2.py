import json

from pywss import Pyws
from pywss.middlewares import DaemonMiddleware
from pywss.public import ERROR_FLAG
from pywss.connector import ConnectManager
from pywss.route import *


class AuthenticationMiddleware(DaemonMiddleware):

    def process_input(self, request, input_msg):
        json_data = json.loads(input_msg)
        if 'name' in json_data:
            return str(json_data['name']), 1


@route('/test/example/2')
def example_2(request, data):
    data = json.loads(data)
    if 'name' in data and 'msg' in data:
        if ConnectManager.send_to_connector(data['name'], data['msg']):
            msg = {'state': 1, 'msg': 'success'}
        else:
            msg = {'state': 0, 'msg': '用户不存在或系统内部异常'}
    else:
        request.ws_send({'state': 0, 'msg': '请求数据参数错误'})
        msg = ERROR_FLAG
    return msg


if __name__ == '__main__':
    ws = Pyws(__name__, address='127.0.0.1', port=8866)
    ws.add_middleware(AuthenticationMiddleware)
    ws.serve_forever()

"""
/* Client1 Code */
ws1 = new WebSocket("ws://127.0.0.1:8866/test/example/2");
ws1.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws1.onclose = function (ev) {
    console.log('Connect Closed')
}
ws1.send(JSON.stringify({'name': 'test1'}))  // you will Authentication first

/* Client2 Code */
ws2 = new WebSocket("ws://127.0.0.1:8866/test/example/2");
ws2.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws12.onclose = function (ev) {
    console.log('Connect Closed')
}
ws2.send(JSON.stringify({'name': 'test2'}))  // you will Authentication first

/* other */

"""
