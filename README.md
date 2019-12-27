## Pywss - Web Socket Server By Python

A WebSocket-Server framework developed similar to Flask


 ```how to install: pip install pywss```


Server code: 
```
from pywss import Pywss, json, ConnectManager

ws = Pywss(__name__, ssl_pem="www.czasg.xyz.pem", ssl_key="www.czasg.xyz.key")


@ws.route('/ws/chat')
def ws_chat(request, data):
    json_data = json.loads(data)
    if json_data.get('start') == True:
        request.conn.send_to_all({'online': ConnectManager.online()})
        return {'sock_id': request.conn.name}
    msg = json_data.get('msg')
    if msg:
        request.conn.send_to_all({'from': request.conn.name, 'msg': msg})


@ws.after_request
def broadcast(): ConnectManager.send_to_all({'online': (ConnectManager.online() or 1) - 1})


if __name__ == '__main__':
    ws.serve_forever()
```
