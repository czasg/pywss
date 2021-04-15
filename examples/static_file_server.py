# coding: utf-8
import pywss

if __name__ == '__main__':
    app = pywss.Pywss()
    app.static("/static")
    app.run()
