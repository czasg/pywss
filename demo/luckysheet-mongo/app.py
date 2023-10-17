# coding: utf-8
import api
import pywss
import threading
import service.update


def start_update_worker():
    threading.Thread(
        target=service.update.update_worker,
        daemon=True,
    ).start()


def main():
    # 初始化 app
    app = pywss.App()
    # 注册静态资源
    app.static("/static", "./static")
    app.get("/", lambda ctx: ctx.redirect("/static/luckysheet.html"))
    # 注册 luckysheet 路由
    api.register(app)
    # 启动更新线程
    start_update_worker()
    # 启动服务
    app.run()


if __name__ == '__main__':
    main()
    """ 浏览器访问 ctrl+左键
    http://localhost:8080
    http://localhost:8080/static/luckysheet.html
    """
