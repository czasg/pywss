# coding: utf-8
import re
import loggus

from pywss.handlers.static import newStaticHandler
from pywss.handlers.websocket import WebSocketHandler


class _RouteMap:

    def __init__(self):
        self.__staticRouteMap = {}
        self.__dynamicRouteList = []
        self.__staticDirRouteList = []

    def register(self, route, *handlers):
        if "(?P<" in route:
            regex = re.sub("(\?P<.*?>)\)", "\\1[^/?]*?)", route) + "/?$"
            prefix = re.search("(.*?)\(\?P", route).group(1)
            length = route.count("/")
            self.__dynamicRouteList.append((prefix, length, re.compile(regex).match, handlers))
        else:
            self.__staticRouteMap[route] = handlers

    def registerDir(self, route, *handlers):
        self.__staticDirRouteList.append((route, handlers))

    def search(self, route):
        inPath = f"{route.strip('/')}"
        if inPath in self.__staticRouteMap:
            return {}, self.__staticRouteMap[inPath], None
        for dirRoute, handlers in self.__staticDirRouteList:
            if inPath.startswith(dirRoute):
                return {"path": inPath.strip(dirRoute)}, handlers, None
        inLength = inPath.count("/")
        for index in range(len(self.__dynamicRouteList)):
            prefix, length, match, handlers = self.__dynamicRouteList[index]
            if length == inLength and inPath.startswith(prefix):
                pathMatch = match(inPath)
                if pathMatch:
                    return pathMatch.groupdict(), handlers, None
        return None, None, "404 by pywss"


RouteMap = _RouteMap()


class Route:

    def __init__(self, route=""):
        self.route = f"/{route.strip().strip('/')}" if route else route
        self.handlers = []
        self.log = loggus.withFields({"module": "Route", "route": route})

    def use(self, *handlers):
        self.handlers += list(handlers)

    def party(self, route, *handlers):
        if not route:
            self.use(*handlers)
            return self
        route = Route(f"{self.route}/{route.strip().strip('/')}")
        handlers = self.handlers + list(handlers)
        route.use(*handlers)
        return route

    def __register(self, method, route, *handlers):
        if not handlers:
            return self.log.warning(f"undefined handlers")
        if not route:
            return self.log.warning(f"undefined route")
        route = route.strip().strip("/")
        route = f"{method}{self.route}/{route}"
        handlers = self.handlers + list(handlers)
        RouteMap.register(route, *handlers)

    def handleDir(self, route, *handlers, root=".", method="GET"):
        route = route.strip().strip("/")
        route = f"{method}{self.route}/{route}"
        handlers = self.handlers + list(handlers)
        handlers.append(newStaticHandler(root))
        RouteMap.registerDir(route, *handlers)

    def get(self, route, *handlers):
        self.__register("GET", route, *handlers)

    def head(self, route, *handlers):
        self.__register("HEAD", route, *handlers)

    def post(self, route, *handlers):
        self.__register("POST", route, *handlers)

    def put(self, route, *handlers):
        self.__register("PUT", route, *handlers)

    def delete(self, route, *handlers):
        self.__register("DELETE", route, *handlers)

    def options(self, route, *handlers):
        self.__register("OPTIONS", route, *handlers)

    def patch(self, route, *handlers):
        self.__register("PATCH", route, *handlers)

    def websocket(self, route, *handlers):
        route = route.strip().strip("/")
        route = f"GET{self.route}/{route}"
        handlers = [WebSocketHandler] + self.handlers + list(handlers)
        RouteMap.register(route, *handlers)
