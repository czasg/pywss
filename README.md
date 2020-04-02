## Pywss - Web Socket Server By Python

A WebSocket-Server framework. it contains `threading` and `asyncio` modules.  
you can use threading module by `Pyws`,  
if you can program asynchronously, you can also use asyncio module by `AsyncPyws`.  

if server want to send msg to client by polling, you can use `radio` middleware.


> pip install:   
> ```pip install pywss (lasted version is 0.0.14)```  
> v0.0.14 add before_first_request & before_request  
> v0.0.13 add asyncio support
 
#### [chatting-room-demo](http://czaorz.gitee.io/static/html/pywss-demo1.html)

#### Using threading
```python
from pywss import Pyws

ws = Pyws(__name__)

@ws.route('/test/example/1/1')
def example_1(request, data):
    request.ws_send({"msg": "hello, example_1"})  # send to yourself
    request.ws_send_to_all({"from": "example_1"})  # send to all conn
    return 'hello, pywss ' + data  # same as to request.ws_send

if __name__ == '__main__':
    ws.serve_forever()
```
**Client (Open Chrome -> F12 -> Console)**
```javascript
ws = new WebSocket("ws://127.0.0.1:8866/test/example/1/1");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
ws.onopen = function() {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send('hello, pywss!')
    }
}
```

#### Using asyncio
```python
import asyncio
from pywss import AsyncPyws

ws = AsyncPyws(__name__)

@ws.route('/test/example/2')
def example_2(request, data):
    return "return directly"

@ws.route('/test/example/3')
async def example_3(request, data):
    await asyncio.sleep(3)
    return "return after sleep(3)"

if __name__ == '__main__':
    ws.serve_forever()
```

#### Using Radio 
```python
from pywss import Pyws, RadioMiddleware

ws = Pyws(__name__)

class Radio(RadioMiddleware):
    RADIO_TIME = 0.5

    def process_data(self):
        return "this is a radio data"

@ws.route('/test/example/3')
def example_3(request, data):
    """There Nothing To Do"""

if __name__ == '__main__':
    ws.add_middleware(Radio)
    ws.serve_forever()
```

```python
from pywss import AsyncPyws, AsyncRadioMiddleware

ws = AsyncPyws(__name__)

class Radio(AsyncRadioMiddleware):
    RADIO_TIME = 0.5

    def process_data(self):
        return "you can also use async here"

@ws.route('/test/example/4')
def example_4(request, data):
    """There Nothing To Do"""

if __name__ == '__main__':
    ws.add_middleware(Radio)
    ws.serve_forever()
```

#### Using SSL
```python
from pywss import Pywss, route

@route("/ws/chat")
def index(request, data):
    return "Pywss support wss protocol"

if __name__ == '__main__':
    ws = Pywss(__name__,
               address="0.0.0.0",
               port=8866,
               ssl_key="www.czasg.xyz.key",
               ssl_pem="www.czasg.xyz.pem")
    ws.serve_forever()
```

## History
* 0.0.14
    * 添加`before_first_request`，首次建立连接后，仅起一次作用。即可理解为处理首次连接传递的数据。  
    一般可用作某些认证机制。
    ```python
    from pywss import AsyncPyws
  
    ws = AsyncPyws(__name__)
  
    @ws.before_first_request
    def first_connect_process(request, data):
      if data != "password":
          request.close()
      return "from before_first_request"
  
    @ws.route('/test')
    def test(request, data):
      return data
    ```
    * 添加`before_reuqest`，每次接收数据时，会先执行此处所注册的函数。  
    **若某个函数返回非空，则不继续往后执行，而是直接返回**  
    可以用作心跳的响应等。
    ```python
    from pywss import AsyncPyws
    
    ws = AsyncPyws(__name__)
    
    @ws.before_request
    def before_process(request, data):
      if data == "ping":
          return "pong"
    
    @ws.route('/test')
    def test(request, data):
      return data
    ```
* 0.0.13
    * 引入asyncio异步模块，保留threading版本
    * 移除中间件模块，仅保留radio
    * 移除公共配置模块
    * 修复TCP粘包与拆包
