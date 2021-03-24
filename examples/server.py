# coding: utf-8
import time
import pywss


def hello(ctx):
    ctx.write("hello world")


def middleware(ctx):
    start = time.time()
    # 中间件调用 next 函数则会进入下一阶段的 handler 处理
    ctx.next()
    ctx.log().withField("cost", time.time() - start).info()


def run():
    # 实例化一个 Pywss 对象
    app = pywss.Pywss()
    # 注册中间件，use会在该路由中全局注册，party同理
    app.use(middleware)
    # 注册路由
    app.get("/hello", hello)
    # 启动服务
    app.run()


if __name__ == '__main__':
    run()
