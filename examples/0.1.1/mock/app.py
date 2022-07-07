# coding: utf-8
import time
import pywss


def log_handler(ctx: pywss.Context):
    start = time.time()
    ctx.next()
    cost = f"{time.time() - start:.3f}"
    code = ctx.response_status_code
    if code < 300:
        ctx.log.variables(cost).info(code)
    elif code < 400:
        ctx.log.variables(cost).warning(code)
    else:
        ctx.log.variables(cost).error(code)


def mock(ctx: pywss.Context):
    # 获取响应码
    code = int(ctx.params.get("code", 200))
    # 获取响应body
    body = ctx.params.get("body", "")
    # 获取响应type
    _type = ctx.params.get("type", "text")
    if _type == "json":
        ctx.set_content_type("application/json")
    ctx.set_status_code(code)
    ctx.write_text(body)


if __name__ == '__main__':
    # 初始化app
    app = pywss.App()
    # 注册全局中间件
    app.use(log_handler)
    # 注册路由
    app.get("/mock", mock)
    # 服务启动
    app.run()
