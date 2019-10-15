## Pywss - Web Socket Server By Python

一种类似Flask开发的WebSocket-Server服务端框架


 ```安装: pip install pywss```

### [example1](https://github.com/CzaOrz/Pywss/blob/master/examples/example1.py)

**Server** (详情见example1.py)

* 函数参数简介
   * /test/example/1: 请求路径
   * request: socket句柄
   * data: 传递过来的数据
* 功能简介
   * 大致就是你发一句话，他立马回你原话+后缀的意思
   * 服务端代码直接用浏览器的控制台就行
```
from pywss import Pyws, route

@route('/test/example/1')
def example_1(request, data):
    return data + ' - data from pywss'

if __name__ == '__main__':
    ws = Pyws(__name__, address='127.0.0.1', port=8866)
    ws.serve_forever()
```
**Client (运行平台: Chrome -> F12 -> console)**
```
ws = new WebSocket("ws://127.0.0.1:8866/test/example/1");
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
### [example2](https://github.com/CzaOrz/Pywss/blob/master/examples/example2.py)

**Server**
* 参数简介
   * RadioMiddleware: 广播中间件，加载此中间件，则会挂起线程轮询发送数据
* 功能简介
   * 在建立连接后，广播数据给所有连接 (其实就是while+for一个一个遍历==僵硬)
```
from pywss import Pyws, route, RadioMiddleware

class Radio(RadioMiddleware):
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
```

**Client**

```
ws = new WebSocket("ws://127.0.0.1:8866/test/example/2");
ws.onmessage = function (ev) {
    console.log(JSON.parse(ev.data));
}
ws.onclose = function (ev) {
    console.log('Connect Closed')
}
```
---
#### [example3](https://github.com/CzaOrz/Pywss/blob/master/examples/example3.py): 认证中间件例子
#### [example4](https://github.com/CzaOrz/Pywss/blob/master/examples/example4.py): 数据中间件例子
#### [example5](https://github.com/CzaOrz/Pywss/blob/master/examples/example5.py): 点对点交流例子

### 框架流程图
*有水印，将就看下*
![pywss](images/pywss.png)