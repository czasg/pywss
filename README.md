## Pywss - Web Socket Server By Python

A WebSocket-Server framework developed similar to Flask


 ```how to install: pip install pywss (lasted version is 0.0.11)```
 
##### Demo: [Web-Socket-Client-Page](https://czaorz.github.io/Pywss/client)
 
 ### Frame flow chart
**[1、frame flow chart](https://www.jianshu.com/p/589022ee5f5c)**

![pywss](https://ae01.alicdn.com/kf/H9aa635519da043209fbd51fe04ad342a1.png)


### [example1](https://github.com/CzaOrz/Pywss/blob/master/examples/example1.py): 基本的交互实现
**Server** (详情见example1.py)
* 参数简介
    * /test/example/1: 请求路径path
    * request: socket句柄，包括发送和接受数据。 
        * 接受数据 request.ws_recv(1024)
        * 发送数据 request.ws_send(data) 
    * data: 传递过来的数据
* 功能简介
   * 客户端发送数据，服务端立即响应并回复，原数据+指定后缀' - data from pywss'
   * 服务端代码直接用浏览器的控制台就行

**提供两种方法交互**
1、request.ws_send    
2、request.conn.send_to_all   

```python
from pywss import Pyws

ws = Pyws(__name__)

@ws.route('/test/example/1/1')
def example_1(request, data):
    return data + ' - data from pywss'

@ws.route('/test/example/1/2')
def example_1(request, data):
    request.ws_send(data + ' - data from pywss')  # 调用ws_send发送消息

@ws.route('/test/example/1/3')
def example_1(request, data):
    request.conn.send_to_all(data + ' - data from pywss')  # 调用send_to_all发送给所有用户

if __name__ == '__main__':
    ws.serve_forever()
```
**Client (运行平台: Chrome -> F12 -> console)**
```html
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
```
---
### [example2](https://github.com/CzaOrz/Pywss/blob/master/examples/example2.py): 广播中间件的实现
**Server**
* 参数简介
   * RadioMiddleware: 广播中间件，加载此中间件，每当有新的连接建立，都会对其进行广播
* 功能简介
   * 在建立连接后，每隔一定之间，广播数据给所有连接
```python
from pywss import Pyws, RadioMiddleware, PublicConfig

PublicConfig.RADIO_TIME = 10  # 控制广播中间件间隔为10s
ws = Pyws(__name__)

class Radio(RadioMiddleware):
    @classmethod
    def process_data(cls):
        return 'Hello, Welcome To Pywss-Radio'  # 返回指定消息

@ws.route('/test/example/2')
def example_2(request, data):
    """There Nothing To Do"""

if __name__ == '__main__':
    ws.add_middleware(Radio)
    ws.serve_forever()
```
**Client**
```html
ws = new WebSocket("ws://127.0.0.1:8866/test/example/2");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
```
---
#### [example3](https://github.com/CzaOrz/Pywss/blob/master/examples/example3.py): 认证中间件的实现
**Server**
* 参数简介
    * DaemonMiddleware: 每当连接建立后，会执行且仅执行一次此中间件，可用于对连接的验证等情况
        * 在此example3中，连接建立后，客户端需要发送一次数据进行验证，数据中需要携带 'name'关键字作用用户名，否则此连接无实际作用
* 功能简介
    * 实现基本的验证功能。即建立连接后，客户端仍需发送一次请求数据，来通过对应验证
```python
import json
from pywss import Pyws, DaemonMiddleware, AuthenticationError

ws = Pyws(__name__)

class AuthenticationMiddleware(DaemonMiddleware):
    @classmethod
    def process_input(self, request, input_msg):
        json_data = json.loads(input_msg)
        if 'name' in json_data:
            return str(json_data['name']), 1
        raise AuthenticationError

@ws.route('/test/example/3')
def example_3(request, data):
    """There Nothing To Do"""

if __name__ == '__main__':
    ws.add_middleware(AuthenticationMiddleware)
    ws.serve_forever()
```
**Client**
```html
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
```
---
#### [example4](https://github.com/CzaOrz/Pywss/blob/master/examples/example4.py): 数据中间件的实现
**Server**
* 参数简介
    * DataMiddleware: 每一次数据传进来时都会进行处理, 可以用作对常见数据进行预处理
* 功能简介
    * 实现每次连接后，对待传递数据的预处理
```python
import json
from pywss import Pyws, route, DataMiddleware

class DataProcessMiddleware(DataMiddleware):
    """
    每一次数据传进来时都会进行处理
    可以用作对常见数据进行预处理
    """
    @classmethod
    def process_input(cls, request, input_msg):
        return json.loads(input_msg)

@route('/test/example/4')
def example_4(request, data):
    print(type(data))

if __name__ == '__main__':
    ws = Pyws(__name__, address='127.0.0.1', port=8866)
    ws.add_middleware(DataProcessMiddleware)
    ws.serve_forever()
```
**Client**
```html
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
```

#### [example5](https://github.com/CzaOrz/Pywss/blob/master/examples/example5.py): 点对点交流的实现
参考：https://github.com/CzaOrz/ioco/tree/master/open_source_project/web_socket_chat

#### [example6](https://github.com/CzaOrz/Pywss/blob/master/examples/example6.py): wss认证
ssl证书一般是第三方提供的，以阿里云服务器为例，可以直接在官网申请下载证书，得到 .pem 和 .key 文件。  
使用前确保证书的可用性。以下举例：    
其中，这里的 "www.czasg.xyz.pem" 是指pem文件的路径，此处表示与当前py文件同目录！  
examples目录已提供过期证书....可以尝试下。
```python
import logging
from pywss import Pywss, json, ConnectManager

ws = Pywss(
    __name__, 
    ssl_pem="www.czasg.xyz.pem", 
    ssl_key="www.czasg.xyz.key", 
    logging_level=logging.WARNING
)

@ws.route('/ws/chat')
def ws_chat(request, data):
    json_data = json.loads(data)
    if json_data.get('start') == True:  # 接收start指令
        # 更新所有已建立连接的socket的当前在线人数
        request.conn.send_to_all({'online': ConnectManager.online()})
        return {'sock_id': request.conn.name}  # 返回自身唯一sock_id
    msg = json_data.get('msg')
    if msg:  # 获取聊天消息，发送给所有已建立连接的socket
        request.conn.send_to_all({'from': request.conn.name, 'msg': msg})

@ws.after_request
def broadcast(): 
    ConnectManager.send_to_all({'online': (ConnectManager.online() or 1) - 1})


if __name__ == '__main__':
    ws.serve_forever()
```
