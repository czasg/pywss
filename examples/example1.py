from pywss import Pyws

ws = Pyws(__name__)


@ws.route('/test/example/1/1')
def example_1(request, data):
    return data + ' - data from pywss'


@ws.route('/test/example/1/2')
def example_1(request, data):
    request.ws_send(data + ' - data from pywss')


@ws.route('/test/example/1/3')
def example_1(request, data):
    request.conn.send_to_all(data + ' - data from pywss')


if __name__ == '__main__':
    ws.serve_forever()

"""
/* Client Code */
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

/* other */
ws.send('hello, pywss!')  // you will get 'hello, pywss! - data from pywss'
"""
