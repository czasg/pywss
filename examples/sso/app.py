# coding: utf-8
import pywss

from api import registerAPI
from middleware.log import logCost
from middleware.trace import trace


def main():
    app = pywss.Pywss()
    app.use(logCost, trace)
    registerAPI(app)
    app.run()


if __name__ == '__main__':
    main()
