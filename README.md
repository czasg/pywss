## Pywss - Web Socket Server By Python

一种类似Flask开发的WebSocket-Server服务端框架

 ```安装: pip install pywss```

#### example1
```
from pywss import Pyws
from pywss.route import route

@route('/test/example/1')
def example_1(request, data):
    return data + ' - data from pywss'

if __name__ == '__main__':
    ws = Pyws(__name__, address='127.0.0.1', port=8866)
    ws.serve_forever()
```




### 框架流程图
![pywss](images/pywss.png)