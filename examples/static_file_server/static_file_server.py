# coding: utf-8
import time
import pywss


def middleware(ctx):
    start = time.time()
    ctx.next()
    ctx.log().withFields({"cost": time.time() - start}).info("exit")


def run():
    app = pywss.Pywss()
    # 注册静态文件服务器相关的路由，并使用中间件
    app.handleDir("/static", middleware, root="./static")
    app.run()


if __name__ == '__main__':
    run()
