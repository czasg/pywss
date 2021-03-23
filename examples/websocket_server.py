# coding: utf-8
import time
import pywss


def AIChat(ctx):
    print("AIChat receive: ", ctx.body())
    ctx.ws(ctx.body().replace(b"!", b"?"))


if __name__ == '__main__':
    app = pywss.Pywss()
    app.websocket("/AIChat", AIChat)
    app.run()

"""
ws = new WebSocket("ws://127.0.0.1:8080/test");
ws.onmessage = function (ev) {
    console.log(ev.data);
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
