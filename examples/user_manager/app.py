# coding: utf-8
import time
import pywss

from api import registerV1


def logMiddleware(ctx):
    start = time.time()
    ctx.next()
    ctx.log().info(f"cost: {time.time() - start}")


def main():
    app = pywss.Pywss()
    # 注册全局中间件
    app.use(logMiddleware)
    # 注册v1路由
    registerV1(app.party("/api/v1"))
    # 启动
    app.run()


if __name__ == '__main__':
    main()
