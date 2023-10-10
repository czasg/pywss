# luckysheet apache2

### 1、配置host文件
以 windows 系统为例，修改：C:\Windows\System32\drivers\etc\host 文件

新增：
```text
127.0.0.1  luckysheet.com
```

### 2、启动容器 
```commandline
docker-compose up
```

### 3、浏览器访问
[http://luckysheet.com](http://luckysheet.com)

4、打开多个浏览器端口，即可完成在线编辑
