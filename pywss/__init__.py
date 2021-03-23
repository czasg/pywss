# coding: utf-8
from pywss.route import Route
from pywss.wsgi import run


class Pywss(Route):

    def run(self, host="0.0.0.0", port=8080):
        run(host, port)
