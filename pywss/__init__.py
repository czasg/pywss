# coding: utf-8
import os
import re
import json
import time
import loggus
import socket
import threading
import selectors

from _io import BufferedReader
from types import FunctionType
from datetime import timedelta
from importlib import import_module
from collections import defaultdict
from pywss.headers import *
from pywss.constant import *
from pywss.middleware import *
from pywss.websocket import WebSocketUpgrade
from pywss.testing import HttpTestRequest, HttpTestResponse
from pywss.closing import Closing
from pywss.routing import Route
from pywss.openapi import openapi_ui_template, merge_dict, parameters_filter

__version__ = '0.1.18'


class Context:
    _handler_index = 0
    _flush_header = False
    _stream = False

    def __init__(
            self, app, log,
            fd, rfd, address,
            http_method, http_url, http_version,
            route, route_params, http_headers,
            app_route, handlers
    ):
        # app
        self.app: 'App' = app
        self.log: loggus.Entry = log
        self.fd: socket.socket = fd
        self.rfd: BufferedReader = rfd
        self.address: tuple = address
        # request
        self.method: str = http_method
        self.url: str = http_url  # /route?key=value
        self.url_params: dict = parse_params(http_url)
        self.route: str = route  # /route
        self.route_params: dict = route_params
        self.version: str = http_version
        self.headers: dict = http_headers
        self.cookies: dict = parse_cookies(http_headers)
        self.content_length: int = int(http_headers.get(HeaderContentLength, 0))
        self.content: bytes = b""  # default empty, use self.body() to instead
        # response
        self.response_status_code: int = 200
        self.response_headers: dict = {
            "Server": "Pywss",
            "PywssVersion": __version__,
            HeaderContentLength: 0,
        }
        self.response_body: list = []
        # ctx
        self._route: str = app_route
        self._handlers: list = handlers
        self.data: Data = Data()  # data save for user

    def next(self) -> None:
        if self._handler_index >= len(self._handlers):
            return
        index = self._handler_index
        self._handler_index += 1
        self._handlers[index](self)

    def close(self):
        self.fd.close()

    def json(self):
        return json.loads(self.body().decode())  # not check Content-Type: application/json

    def form(self) -> dict:
        resp = {}
        ct = self.headers.get(HeaderContentType, "").strip()
        body = unquote(self.body().decode()).strip()

        if ct == "application/x-www-form-urlencoded":
            for value in body.split("&"):
                k, v = value.split("=", 1)
                resp[k] = v
            return resp
        elif not ct.startswith("multipart/form-data"):
            raise Exception(f"not support form Content-Type:{ct}")

        # parse form-data boundary
        boundary = ""
        for v in ct.split(";"):
            v = v.strip()
            if v.startswith("boundary="):
                boundary = v[9:].strip('"')
                break
        if not boundary:
            raise Exception(f"invalid form-data, without boundary")
        # parse form-data
        for data in body.split(f"--{boundary}"):
            data = data.strip()
            if not data.startswith(HeaderContentDisposition):
                continue
            h, v = data.split("\r\n\r\n", 1)
            name = ""
            for k in h.split(";"):
                k = k.strip()
                if k.startswith("name="):
                    name = k[5:].strip('"')
                    break
            if not name:
                raise Exception("invalid form-data, without name")
            resp[name] = v
        return resp

    def body(self) -> bytes:
        if self._stream:
            return self.content  # should be empty
        if not self.content and self.content_length:
            self.content = self.rfd.read(self.content_length)
        if not self.content and self.headers.get(HeaderTransferEncoding, "").lower() == "chunked":
            size = int(self.rfd.readline(), 16)
            while size > 0:
                self.content += self.rfd.read(size)
                assert self.rfd.read(2) == b"\r\n"
                size = int(self.rfd.readline(), 16)
            assert self.rfd.read(2) == b"\r\n"
        return self.content

    def stream(self, size=65536):
        if self._stream:
            return self.content  # should be empty
        if not self.content and self.content_length:
            cl = self.content_length
            while cl > 0:
                rl = min(size, cl)
                yield self.rfd.read(rl)
                cl -= rl
            self._stream = True
            return
        if not self.content and self.headers.get(HeaderTransferEncoding, "").lower() == "chunked":
            size = int(self.rfd.readline(), 16)
            while size > 0:
                yield self.rfd.read(size)
                assert self.rfd.read(2) == b"\r\n"
                size = int(self.rfd.readline(), 16)
            assert self.rfd.read(2) == b"\r\n"
            self._stream = True

    def set_header(self, k, v) -> None:
        header = []
        for key in k.split("-"):
            header.append(key[0].upper() + key[1:].lower())
        self.response_headers["-".join(header)] = v

    def set_content_length(self, size: int, inherit=True) -> None:
        if inherit:
            size += self.response_headers.get(HeaderContentLength, 0)
        self.response_headers[HeaderContentLength] = size

    def set_content_type(self, v) -> None:
        self.response_headers.setdefault(HeaderContentType, v)

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
        self.response_headers[HeaderSetCookie] = "; ".join(buf)

    def set_status_code(self, status_code) -> None:
        self.response_status_code = status_code

    def redirect(self, url, status_code=StatusFound) -> None:
        if "?" not in url and "?" in self.url:
            url = f"{url}?{self.url.split('?', 1)[1]}"
        self.set_status_code(status_code)
        self.set_header(HeaderLocation, url)

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

    def write_file(self, file, attachment=False) -> None:
        if isinstance(file, str) and os.path.exists(file):
            if attachment:
                filename = os.path.split(file)[-1]
                self.set_header(HeaderContentDisposition, f'attachment; filename="{filename}"')
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
        self.base_route: str = f"/{base_route.strip().strip('/')}" if base_route else base_route
        self.base_handlers: list = list(base_handlers) if base_handlers else []
        self.head_match_routes: list = []
        self.parse_match_routes: list = []
        self.full_match_routes: dict = {}
        self.openapi_data: dict = {
            "paths": defaultdict(dict),
        }
        self.running: bool = False
        self.data: Data = Data()
        self.log = loggus.GetLogger()

    def _register(self, method, route, handlers) -> None:
        if len(handlers) < 1:
            raise Exception("not found handlers")
        route = f"/{route.strip().strip('/')}" if route else route
        route = f"{self.base_route}{route}"
        route = f"/{route.strip().strip('/')}"
        route = route.rstrip("/")
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

        def split_method_route(route):
            if "/" not in route:
                return route, "/"
            m, r = route.split("/", 1)
            return m, "/" + r.strip("/")

        for route, v in self.full_match_routes.items():
            if isinstance(v, App):
                continue
            elif "{" in route and "}" in route:
                r = Route.from_route(route)
                self.parse_match_routes.append(
                    (r, v)
                )
                if hasattr(v[-1], "__openapi_path__"):
                    _method, _route = split_method_route(route)
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
                    _method, _route = split_method_route(route)
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
        self._register(MethodGet, route, handlers)
        self._register(MethodHead, route, handlers)

    def get(self, route, *handlers) -> None:
        self._register(MethodGet, route, handlers)

    def post(self, route, *handlers) -> None:
        self._register(MethodPost, route, handlers)

    def head(self, route, *handlers) -> None:
        self._register(MethodHead, route, handlers)

    def put(self, route, *handlers) -> None:
        self._register(MethodPut, route, handlers)

    def delete(self, route, *handlers) -> None:
        self._register(MethodDelete, route, handlers)

    def patch(self, route, *handlers) -> None:
        self._register(MethodPatch, route, handlers)

    def options(self, route, *handlers) -> None:
        self._register(MethodOptions, route, handlers)

    def any(self, route, *handlers) -> None:
        self.get(route, *handlers)
        self.post(route, *handlers)
        self.head(route, *handlers)
        self.put(route, *handlers)
        self.delete(route, *handlers)
        self.patch(route, *handlers)
        self.options(route, *handlers)

    def view(self, route, *handlers):
        if len(handlers) < 1:
            raise Exception("not found handlers")
        view = handlers[-1]
        handlers = list(handlers[:-1])
        if hasattr(view, "use"):
            handlers += list(getattr(view, "use"))
        for method in ("get", "post", "head", "put", "delete", "patch", "options", "any"):
            if hasattr(view, f"http_{method}_use"):
                handlers += list(getattr(view, f"http_{method}_use"))
            if hasattr(view, f"http_{method}"):
                getattr(self, method)(route, *handlers, getattr(view, f"http_{method}"))

    def view_modules(self, path, *handlers, prefix=True):
        if not os.path.exists(path):
            raise Exception(f"{path} not exists")
        for base, _, files in os.walk(path):
            base_modules = re.findall("([a-zA-Z0-9-_{}]+)", base)
            route_modules = base_modules
            if not prefix:
                prefix_length = len(re.findall("([a-zA-Z0-9-_{}]+)", path))
                route_modules = base_modules[prefix_length:]
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                filename = filename[:-3]
                if filename.startswith(("_", "test")) and filename != "__init__":
                    continue
                route = filename.replace("__init__", "")
                module = import_module(".".join([*base_modules, filename]))
                view_name = getattr(module, "__view__", "View")
                view_module = getattr(module, view_name, None)
                if not view_module:
                    continue
                if callable(view_module) and type(view_module) is not FunctionType:
                    view_module = view_module()
                route = getattr(module, "__route__", route).strip("/")
                self.view("/".join([*route_modules, route]), *handlers, view_module)

    def openapi(
            self,
            enable=True,
            title="OpenAPI",
            version="0.0.1",
            openapi_json_route="/docs/openapi.json",
            openapi_ui_route="/docs",
            openapi_ui_js_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.14.0/swagger-ui-bundle.js",
            openapi_ui_css_url="https://cdn.bootcdn.net/ajax/libs/swagger-ui/4.14.0/swagger-ui.css",

    ) -> None:
        if not enable:
            return
        self.openapi_data = {
            "openapi": "3.0.2",
            "info": {
                "title": title,
                "version": version
            },
            "paths": defaultdict(dict),
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                    },
                    "basicAuth": {
                        "type": "http",
                        "scheme": "basic",
                    },
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "X-API-KEY",
                    }
                }
            }
        }
        self.get(openapi_json_route, lambda ctx: ctx.write(self.openapi_data))
        self.get(openapi_ui_route, lambda ctx: ctx.write(openapi_ui_template(
            title,
            f"{self.base_route}/{openapi_json_route.strip('/')}",
            openapi_ui_js_url,
            openapi_ui_css_url,
        )))

    def handler_request(self, request: socket.socket, address: tuple) -> None:
        log = self.log
        try:
            rfd = request.makefile("rb", -1)
            while True:
                http_method, http_url, http_version, err = parse_request_line(rfd)
                if err:
                    request.sendall(b"HTTP/1.1 400 BadRequest\r\n")
                    return
                route = app_route = f"/{http_url.split('?', 1)[0].lstrip('/')}"  # /route
                route_params = dict()
                method_route = f"{http_method.upper()}{route.rstrip('/')}"  # GET/route
                log = log.update(route=method_route)
                http_headers, err = parse_headers(rfd)
                if err:
                    request.sendall(b"HTTP/1.1 400 BadRequest\r\n")
                    log.error(err)
                    return
                # check keep alive
                if http_headers.get(HeaderConnection, "").lower() == "close":
                    break
                # full match
                handlers = self.full_match_routes.get(method_route, None)
                # parser match
                if not handlers:
                    for r, v in self.parse_match_routes:
                        fix, rp = r.match(method_route)
                        if fix:
                            app_route = r.route
                            handlers = v
                            route_params = rp
                            break
                # head match
                if not handlers:
                    for r, v in self.head_match_routes:
                        if method_route.startswith(r):
                            app_route = r
                            handlers = v
                            break
                if not handlers:
                    request.sendall(b"HTTP/1.1 404 NotFound\r\n")
                    log.warning("No Handler")
                    return
                ctx = Context(
                    self, log,
                    request, rfd, address,
                    http_method, http_url, http_version,
                    route, route_params, http_headers,
                    app_route, handlers
                )
                ctx.next()
                ctx.flush()
                if ctx.content_length != len(ctx.content):  # sock should be close
                    return
        except ConnectionAbortedError:
            log.error("connect abort")
        except ConnectionResetError:
            log.error("connect reset")
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
        Closing.add_close(self.close)
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
                        threading.Thread(target=self.handler_request, args=(request, address), daemon=True).start()
            for i in range(grace):
                self.log.update(hit=i + 1, grace=grace).warning("server closing")
                time.sleep(1)
            self.log.warning("server closed")


class Data(dict):

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self.get(item, None)
