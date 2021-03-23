# coding: utf-8
import time
import pywss


def middleware(ctx):
    start = time.time()
    ctx.next()
    print(f"cost: {time.time() - start}")


def run():
    app = pywss.Pywss()
    # 注册静态文件服务器相关的路由，并使用中间件
    app.handleDir("/static", middleware, root=".")
    app.run()


if __name__ == '__main__':
    run()
