# coding: utf-8
import re
import pywss


def aiChat(ctx):
    data = ctx.body(str)
    ctx.ws(re.sub("[吗?？]", "!", data))


def say(ctx):
    data = ctx.queryParams().get("say", "啥也没说")
    ctx.wsAll(data)


if __name__ == '__main__':
    app = pywss.Pywss()
    app.websocket("/chat", aiChat)
    app.get("/say", say)
    app.run()

"""
ws = new WebSocket("ws://127.0.0.1:8080/chat");
ws.onmessage = function (ev) {
    console.log(ev.data);
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
ws.onopen = function() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send('hello??')  // you will get 'hello, pywss! - data from pywss'
    }
}
"""
