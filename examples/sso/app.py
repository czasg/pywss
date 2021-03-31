# coding: utf-8
import pywss

from api import registerAPI
from middleware.log import logCost
from middleware.trace import trace
from pywss.statuscode import StatusNoContent


def main():
    app = pywss.Pywss()
    app.use(logCost, trace)
    # 探活接口
    app.get("/liveness", lambda ctx: ctx.setStatusCode(StatusNoContent))
    # prometheus支持
    app.get("/metrics", lambda ctx: ctx.setStatusCode(StatusNoContent))
    # 注册路由
    registerAPI(app.party("/api"))
    app.run()


if __name__ == '__main__':
    main()
