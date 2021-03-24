# coding: utf-8
import loggus

from pywss.route import Route
from pywss.wsgi import run


class Pywss(Route):

    def run(self, host="0.0.0.0", port=8080):
        log = loggus.withFields({"host": host, "port": port})
        with log.withTraceback():
            log.info("server start")
            run(host, port)
