# coding: utf-8
import pywss


def hello(ctx: pywss.Context):
    ctx.write({
        "hello": ctx.paths["name"],
        "file": __file__,
    })


if __name__ == '__main__':
    # 初始化 app
    app = pywss.App()
    # 注册路由并绑定匿名函数
    app.get("/hello", lambda ctx: ctx.write("hello world"))
    # 注册路由并绑定hello
    app.get("/hello/{name}", hello)
    # 启动服务
    app.run()
    """ 浏览器访问 ctrl+左键
    http://localhost:8080/hello
    http://localhost:8080/hello/world
    """
