from pywss import Pyws, route, RadioMiddleware, PublicConfig

PublicConfig.RADIO_TIME = 1  # 控制广播中间件间隔


class Radio(RadioMiddleware):
    """
    这个会在主线程挂起，每隔一定时间会循环对所有用户发送消息
    """

    @classmethod
    def process_data(cls):
        return 'Hello, Welcome To Pywss-Radio'


@route('/test/example/2')
def example_2(request, data):
    """There Nothing To Do"""


if __name__ == '__main__':
    ws = Pyws(__name__, address='127.0.0.1', port=8866)
    ws.add_middleware(Radio)
    ws.serve_forever()

"""
/* Client Code */
ws = new WebSocket("ws://127.0.0.1:8866/test/example/2");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
"""
