from pywss import Pyws

ws = Pyws(__name__)


@ws.route('/test/example/1/1')
def example_1(request, data):
    request.ws_send({"msg": "hello, example_1"})  # send to yourself
    request.ws_send_to_all({"from": "example_1"})  # send to all conn
    return 'hello, pywss ' + data  # same as to request.ws_send


if __name__ == '__main__':
    ws.serve_forever()

"""
ws = new WebSocket("ws://127.0.0.1:8866/test/example/1/1");
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
