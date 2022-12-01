# coding: utf-8
import os, re
import json
import time
import loggus
import socket
import threading
import selectors

from _io import BufferedReader
from datetime import timedelta
from collections import defaultdict
from pywss.headers import *
from pywss.statuscode import *
from pywss.websocket import WebSocketUpgrade, WebSocketContextWrap
from pywss.testing import HttpTestRequest, HttpTestResponse
from pywss.static import NewStaticHandler
from pywss.closing import Closing
from pywss.routing import Route
from pywss.openapi import openapi_ui_template, merge_dict, parameters_filter

__version__ = '0.1.12'


class Context:
    _handler_index = 0
    _flush_header = False

    def __init__(self, app, fd, address, log, rfd, method, path, paths, version, headers, route, handlers):
        self.app: 'App' = app
        self.log: loggus.Entry = log
        self.fd: socket.socket = fd
        self.rfd: BufferedReader = rfd
        self.method: str = method
        self.version: str = version
        self.headers: dict = headers
        self.cookies: dict = parse_cookies(headers)
        self.path: str = path
        self.paths: dict = paths
        self.params: dict = parse_params(path)
        self.route: str = route
        self._handlers: list = handlers
        self.address: tuple = address
        self.data: Data = Data()  # data save for user

        self.content_length: int = int(headers.get("Content-Length", 0))
        self.content: bytes = b""  # default empty, use self.body() to instead

        self.response_status_code: int = 200
        self.response_headers: dict = {
            "Server": "Pywss",
            "PywssVersion": __version__,
            "Content-Length": 0,
        }
        self.response_body: list = []

    def next(self) -> None:
        if self._handler_index >= len(self._handlers):
            return
        index = self._handler_index
        self._handler_index += 1
        self._handlers[index](self)

    def json(self):
        return json.loads(self.body().decode())  # not check Content-Type: application/json

    def form(self) -> dict:
        resp = {}
        ct = self.headers.get("Content-Type").strip()

        if ct == "application/x-www-form-urlencoded":
            for value in self.body().decode().strip().split("&"):
                k, v = value.split("=", 1)
                resp[unquote(k)] = unquote(v)
            return resp
        elif not ct.startswith("multipart/form-data"):
            raise Exception(f"not support form Content-Type:{ct}")

        # parse form-data boundary
        boundary = ""
        for v in ct.split(";"):
            v = v.strip()
            if v.startswith("boundary="):
                boundary = v.replace("boundary=", "")
                break
        if not boundary:
            raise Exception(f"invalid form-data, with not boundary")
        # parse form-data
        for data in self.body().decode().split(f"--{boundary}"):
            data = data.strip()
            if not data.startswith("Content-Disposition"):
                continue
            h, v = data.split("\r\n\r\n", 1)
            name = re.search("name=\"(.*?)\"", h).group(1)
            resp[name] = v
        return resp

    def body(self) -> bytes:
        if not self.content and self.content_length:
            self.content = self.rfd.read(self.content_length)
        return self.content

    def set_header(self, k, v) -> None:
        header = []
        for key in k.split("-"):
            header.append(key[0].upper() + key[1:].lower())
        self.response_headers["-".join(header)] = v

    def set_content_length(self, size: int) -> None:
        self.response_headers["Content-Length"] = self.response_headers.get("Content-Length", 0) + size

    def set_content_type(self, v) -> None:
        self.response_headers.setdefault("Content-Type", v)

    def set_cookie(
            self, key, value, maxAge=None, expires=None, path="/", domain=None, secure=False, httpOnly=False
    ) -> None:
        buf = [f"{key}={value}"]
        if isinstance(maxAge, timedelta):
            maxAge = (maxAge.days * 60 * 60 * 24) + maxAge.seconds
        if expires is not None:
            expires = time.gmtime(expires)
        elif maxAge is not None:
            expires = time.gmtime(time.time() + maxAge)
        if expires:
            d = expires
            expires = "%s, %02d%s%s%s%04d %02d:%02d:%02d GMT" % (
                ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")[d.tm_wday],
                d.tm_mday,
                "-",
                (
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                )[d.tm_mon - 1],
                "-",
                d.tm_year,
                d.tm_hour,
                d.tm_min,
                d.tm_sec,
            )

        for k, v, q in (
                ("Domain", domain, True),
                ("Expires", expires, False),
                ("Max-Age", maxAge, False),
                ("Secure", secure, None),
                ("HttpOnly", httpOnly, None),
                ("Path", path, False),
        ):
            if q is None:
                if v:
                    buf.append(k)
                continue
            if v is None:
                continue
            buf.append(f"{k}={v}")
        self.response_headers["Set-Cookie"] = "; ".join(buf)

    def set_status_code(self, status_code) -> None:
        self.response_status_code = status_code

    def redirect(self, url, status_code=StatusFound) -> None:
        if "?" not in url and "?" in self.path:
            url = f"{url}?{self.path.split('?', 1)[1]}"
        self.set_status_code(status_code)
        self.set_header("Location", url)

    def write(self, body) -> None:
        if isinstance(body, (str, bytes)):
            self.write_text(body)
        elif isinstance(body, (dict, list)):
            self.write_json(body)
        elif isinstance(body, BufferedReader):
            self.write_file(body)

    def write_text(self, data: str) -> None:
        if isinstance(data, str):
            data = data.encode()
        self.set_content_length(len(data))
        self.set_content_type("text/html; charset=utf-8")
        self.response_body.append(data)

    def write_json(self, data) -> None:
        data = json.dumps(data, ensure_ascii=False).encode()
        self.set_content_length(len(data))
        self.set_content_type("application/json")
        self.response_body.append(data)

    def write_file(self, file) -> None:
        if isinstance(file, str) and os.path.exists(file):
            file = open(file, "rb")
        if not isinstance(file, BufferedReader):
            raise Exception("invalid file type")
        self.set_content_length(os.stat(file.fileno())[6])
        self.response_body.append(file)

    def ws_read(self) -> bytes:  # impl by WebSocketUpgrade
        raise NotImplementedError

    def ws_write(self, body) -> None:  # impl by WebSocketUpgrade
        raise NotImplementedError

    def flush(self) -> None:
        if not self._flush_header:
            data = [f"{self.version} {self.response_status_code} Pywss"]
            for k, v in self.response_headers.items():
                data.append(f"{k}: {v}")
            data = "\r\n".join(data) + "\r\n\r\n"
            self.fd.sendall(data.encode())
            self._flush_header = True
        for body in self.response_body:
            if isinstance(body, bytes):
                self.fd.sendall(body)
            elif isinstance(body, str):
                self.fd.sendall(body.encode())
            elif isinstance(body, BufferedReader):
                chunk = body.read(8192)
                while chunk:
                    self.fd.sendall(chunk)
                    chunk = body.read(8192)
                body.close()
        self.response_body = []


class App:

    def __init__(self, base_route="", base_handlers=None):
        self.base_route = f"/{base_route.strip().strip('/')}" if base_route else base_route
        self.base_handlers = list(base_handlers) if base_handlers else []
        self.head_match_routes = []
        self.parse_match_routes = []
        self.full_match_routes = {}
        self.log = loggus.GetLogger()
        self.openapi_data = {
            "paths": defaultdict(dict),
        }
        self.running = False
        Closing.add_close(self.close)

    def register(self, method, route, handlers) -> None:
        route = f"/{route.strip().strip('/')}" if route else route
        route = f"{self.base_route}{route}"
        route = f"/{route.strip().strip('/')}"
        self.full_match_routes[f"{method}{route}"] = list(self.base_handlers) + list(handlers)

    def build(self) -> None:
        routes = {}
        for route, v in self.full_match_routes.items():
            if isinstance(v, App):
                v.build()
                routes.update(v.full_match_routes)
                self.head_match_routes += v.head_match_routes
                self.parse_match_routes += v.parse_match_routes
                self.openapi_data = merge_dict(self.openapi_data, v.openapi_data)
        for route, v in self.full_match_routes.items():
            if isinstance(v, App):
                continue
            elif "{" in route and "}" in route:
                r = Route.from_route(route)
                self.parse_match_routes.append(
                    (r, v)
                )
                if hasattr(v[-1], "__openapi_path__"):
                    i = route.index("/")
                    _method, _route = route[:i], route[i:]
                    path = v[-1].__openapi_path__
                    for node in r.route_list:
                        if not node.name:
                            continue
                        if parameters_filter(node.name, path["parameters"]):
                            continue
                        path["parameters"].append({
                            "name": node.name,
                            "in": "path",
                            "required": True,
                        })
                    if _route not in self.openapi_data["paths"]:
                        self.openapi_data["paths"][_route] = {}
                    self.openapi_data["paths"][_route][_method.lower()] = path
                self.log.update({
                    "type": "parsermatch",
                    "route": route,
                    "handlers": [handler.__name__ for handler in v],
                }).info(f"bind route")
            elif route.endswith("*"):
                match = route.strip().rstrip("/*").rstrip("*")
                self.head_match_routes.append((match, v))
                self.log.update({
                    "type": "headmatch",
                    "route": route,
                    "handlers": [handler.__name__ for handler in v],
                }).info(f"bind route")
            else:
                routes[route] = v
                if hasattr(v[-1], "__openapi_path__"):
                    i = route.index("/")
                    _method, _route = route[:i], route[i:]
                    if _route not in self.openapi_data["paths"]:
                        self.openapi_data["paths"][_route] = {}
                    self.openapi_data["paths"][_route][_method.lower()] = v[-1].__openapi_path__
                self.log.update({
                    "type": "fullmatch",
                    "route": route,
                    "handlers": [handler.__name__ for handler in v],
                }).info(f"bind route")
        self.full_match_routes = routes
        self.running = True

    def party(self, route, *handlers) -> 'App':
        route = f"{self.base_route}/{route.strip().strip('/')}"
        if route not in self.full_match_routes:
            self.full_match_routes[route] = App(route, list(self.base_handlers) + list(handlers))
        return self.full_match_routes[route]

    def use(self, *handlers) -> None:
        self.base_handlers += list(handlers)

    def static(self, route, rootDir, *handlers, staticHandler=NewStaticHandler) -> None:
        if not os.path.exists(rootDir):
            raise Exception(f"not found {rootDir}")
        if staticHandler:
            handlers = list(handlers)
            handlers.append(staticHandler(rootDir))
        if not route.endswith("*"):
            route = f"{route.strip().rstrip('/')}/*"
        self.register(MethodGet, route, handlers)
        self.register(MethodHead, route, handlers)

    def get(self, route, *handlers) -> None:
        self.register(MethodGet, route, handlers)

    def post(self, route, *handlers) -> None:
        self.register(MethodPost, route, handlers)

    def head(self, route, *handlers) -> None:
        self.register(MethodHead, route, handlers)

    def put(self, route, *handlers) -> None:
        self.register(MethodPut, route, handlers)

    def delete(self, route, *handlers) -> None:
        self.register(MethodDelete, route, handlers)

    def patch(self, route, *handlers) -> None:
        self.register(MethodPatch, route, handlers)

    def options(self, route, *handlers) -> None:
        self.register(MethodOptions, route, handlers)

    def any(self, route, *handlers) -> None:
        self.get(route, *handlers)
        self.post(route, *handlers)
        self.head(route, *handlers)
        self.put(route, *handlers)
        self.delete(route, *handlers)
        self.patch(route, *handlers)
        self.options(route, *handlers)

    def openapi(
            self,
            title="OpenAPI",
            version="0.0.1",
            openapi_json_route="/openapi.json",
            openapi_ui_route="/docs",
            openapi_ui_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.14.0/swagger-ui-bundle.js",
            openapi_ui_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.14.0/swagger-ui.css",
    ) -> None:
        self.openapi_data = {
            "openapi": "3.0.2",
            "info": {
                "title": title,
                "version": version
            },
            "paths": defaultdict(dict),
        }
        self.get(openapi_json_route, lambda ctx: ctx.write(self.openapi_data))
        self.get(openapi_ui_route, lambda ctx: ctx.write(openapi_ui_template(
            title,
            f"{self.base_route}/{openapi_json_route.strip('/')}",
            openapi_ui_js_url,
            openapi_ui_css_url,
        )))

    def _(self, request: socket.socket, address: tuple) -> None:
        log = self.log
        try:
            rfd = request.makefile("rb", -1)
            while True:
                method, path, version, err = parse_request_line(rfd)
                if err:
                    request.sendall(b"HTTP/1.1 400 BadRequest\r\n")
                    return
                route = f"{method.upper()}/{path.split('?', 1)[0].strip('/')}"
                log = log.update(route=route)
                hes, err = parse_headers(rfd)
                if err:
                    request.sendall(b"HTTP/1.1 400 BadRequest\r\n")
                    log.error(err)
                    return
                # check keep alive
                if hes.get("Connection", "").lower() == "close":
                    break
                # full match
                paths = {}
                handlers = self.full_match_routes.get(route, None)
                # parser match
                if not handlers:
                    for r, v in self.parse_match_routes:
                        fix, ps = r.match(route)
                        if fix:
                            route = r.route
                            handlers = v
                            paths = ps
                            break
                # head match
                if not handlers:
                    for r, v in self.head_match_routes:
                        if route.startswith(r):
                            route = r
                            handlers = v
                            break
                if not handlers:
                    request.sendall(b"HTTP/1.1 404 NotFound\r\n")
                    log.warning("No Handler")
                    return
                ctx = Context(self, request, address, log, rfd, method, path, paths, version, hes, route, handlers)
                ctx.next()
                ctx.flush()
        except ConnectionAbortedError:
            log.error("connect abort")
        except:
            log.traceback()
        finally:
            try:
                request.shutdown(socket.SHUT_WR)
            except OSError:
                pass
            request.close()

    def close(self) -> None:
        self.running = False

    def run(self, host="0.0.0.0", port=8080, grace=0, request_queue_size=5, poll_interval=0.5) -> None:
        self.build()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
            sock.listen(request_queue_size)
            selector = selectors.PollSelector if hasattr(selectors, 'PollSelector') else selectors.SelectSelector
            with self.log.trycache():
                with selector() as _selector:
                    _selector.register(sock.fileno(), selectors.EVENT_READ)
                    self.log.update(
                        version=__version__,
                        host=host,
                        port=port,
                        grace=grace
                    ).info("server start")
                    while self.running:
                        ready = _selector.select(poll_interval)
                        if not ready:
                            continue
                        request, address = sock.accept()
                        threading.Thread(target=self._, args=(request, address), daemon=True).start()
            for i in range(grace):
                self.log.update(hit=i + 1, grace=grace).warning("server closing")
                time.sleep(1)
            self.log.warning("server closed")


class Data(dict):

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item, None)
