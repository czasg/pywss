# coding: utf-8
import os
import re
import sys
import json
import time
import gzip
import queue
import signal
import loggus
import socket
import inspect
import threading
import selectors
from typing import Dict, Union
from _io import BufferedReader
from types import FunctionType
from datetime import timedelta
from importlib import import_module, reload
from collections import defaultdict
from pywss.headers import *
from pywss.constant import *
from pywss.handler import *
from pywss.websocket import WebSocketUpgrade
from pywss.testing import HttpTestRequest, HttpTestResponse
from pywss.routing import Route
from pywss.openapi import openapi_ui_template
from pywss.utils import split_method_route, merge_dict, Query

__version__ = '0.2.4'


class Context:
    _handler_index = 0

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
        self.query: Query = Query(parse_params(http_url))
        self.route: str = route  # /route
        self.route_params: dict = route_params
        self.params: Query = Query(route_params)
        self.version: str = http_version
        self.headers: dict = http_headers
        self.cookies: dict = parse_cookies(http_headers)
        self.content_length: int = int(http_headers.get(HeaderContentLength, 0))
        self.content: bytes = b""  # default empty, use self.body() to instead
        # response
        self.response_status_code: int = 200
        self.response_headers: dict = {
            "X-Server": "Pywss",
            "X-Pywss-Version": __version__,
            HeaderContentLength: 0,
        }
        self.response_body: list = []
        # ctx
        self._route: str = app_route
        self._handlers: list = handlers
        self.data: Data = Data()  # data save for user
        # flush
        self.flush_header = once(self.__flush_header)
        self.flush_body = once(self.__flush_body)

    def next(self) -> None:
        if self._handler_index >= len(self._handlers):
            return
        index = self._handler_index
        self._handler_index += 1
        self._handlers[index](self)

    def close(self) -> None:
        try:
            self.fd.shutdown(socket.SHUT_WR)
        except:
            pass
        self.fd.close()

    def is_closed(self) -> bool:
        try:
            self.fd.recv(0)
            self.fd.send(b"")
            return False
        except:
            return True

    def json(self):
        return json.loads(self.text())  # not check Content-Type: application/json

    def form(self) -> dict:
        resp = {}
        ct = self.headers.get(HeaderContentType, "").strip()
        body = unquote(self.text()).strip()

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

    def file(self) -> Dict[str, 'File']:
        ct = self.headers.get(HeaderContentType, "").strip()
        if not ct.startswith("multipart/form-data"):
            raise Exception(f"not support form Content-Type:{ct}")
        resp = {}
        boundary = ""
        for v in ct.split(";"):
            v = v.strip()
            if v.startswith("boundary="):
                boundary = v[9:].strip('"')
                break
        if not boundary:
            raise Exception(f"invalid form-data, without boundary")
        # parse form-data
        for data in self.body().split(f"--{boundary}".encode()):
            data = data.strip()
            if not data.startswith(HeaderContentDisposition.encode()):
                continue
            h, v = data.split(b"\r\n\r\n", 1)
            h = unquote(h.decode()).strip()
            name = ""
            filename = ""
            headers = {}
            for line in h.split("\r\n"):
                lines = line.split(":", 1)
                if len(lines) != 2:
                    continue
                headerKey = lines[0].strip()
                headerVal = lines[1].strip()
                headers[headerKey] = headerVal
                if headerKey.startswith(HeaderContentDisposition):
                    for val in headerVal.split(";"):
                        val = val.strip()
                        if val.startswith("name="):
                            name = val[5:].strip('"')
                        elif val.startswith("filename="):
                            filename = val[9:].strip('"')
            if not name:
                raise Exception("invalid form-data, without name")
            resp[name] = File(name, filename, headers, v)
        return resp

    def body(self) -> bytes:
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

    def text(self) -> str:
        if "gzip" in self.headers.get(HeaderContentEncoding, ""):
            return gzip.decompress(self.body()).decode()
        return self.body().decode()

    def stream(self, size=65536, readline=False):
        if self.headers.get(HeaderTransferEncoding, "").lower() == "chunked":
            size = int(self.rfd.readline(), 16)
            while size > 0:
                yield self.rfd.read(size)
                assert self.rfd.read(2) == b"\r\n"
                size = int(self.rfd.readline(), 16)
            assert self.rfd.read(2) == b"\r\n"
            return
        cl = self.content_length
        while cl > 0:
            data = self.rfd.readline(cl) if readline else self.rfd.read(min(size, cl))
            yield data
            cl -= len(data)

    def set_header(self, k: str, v: str) -> None:
        self.response_headers[k.title()] = v

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

    def sse_event(self, data, event="message", id=None, retry=None):
        self.flush_header(type="sse")
        if event:
            self.fd.sendall(f"event: {event}\n".encode())
        if data:
            self.fd.sendall(f"data: {data}\n".encode())
        if id:
            self.fd.sendall(f"id: {id}\n".encode())
        if retry:
            self.fd.sendall(f"retry: {retry}\n".encode())
        self.fd.sendall(b"\n")

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

    def write_json(self, data, **kwargs) -> None:
        if not isinstance(data, str):
            data = json.dumps(data, ensure_ascii=False, **kwargs).encode()
        if not isinstance(data, bytes):
            data = data.encode()
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

    def write_chunk(self, data: Union[str, bytes]):
        if isinstance(data, str):
            data = data.encode()
        self.flush_header(type="chunked")
        self.fd.sendall(f"{hex(len(data))[2:]}".encode() + b'\r\n' + data + b'\r\n')

    def ws_read(self) -> bytes:  # impl by WebSocketUpgrade
        raise NotImplementedError

    def ws_write(self, body) -> None:  # impl by WebSocketUpgrade
        raise NotImplementedError

    def flush(self):
        self.flush_header()
        self.flush_body()

    def __flush_header(self, type=None):
        if type == "chunked":
            self.response_headers.pop(HeaderContentLength, None)
            self.response_headers.setdefault(HeaderContentType, "text/html; charset=utf-8")
            self.response_headers.setdefault(HeaderTransferEncoding, "chunked")
        if type == "sse":
            self.response_headers.pop(HeaderContentLength, None)
            self.response_headers.setdefault(HeaderContentType, "text/event-stream")
            self.response_headers.setdefault(HeaderCacheControl, "no-cache")
            self.response_headers.setdefault(HeaderConnection, "keep-alive")
            self.response_headers.setdefault(HeaderAccessControlAllowOrigin, "*")
        data = [f"{self.version} {self.response_status_code} Pywss"]
        for k, v in self.response_headers.items():
            data.append(f"{k}: {v}")
        data = "\r\n".join(data) + "\r\n\r\n"
        self.fd.sendall(data.encode())

    def __flush_body(self):
        if "chunked" in self.response_headers.get(HeaderTransferEncoding, ""):
            self.fd.send(b'0\r\n\r\n')
            return
        for body in self.response_body:
            if isinstance(body, bytes):
                self.fd.sendall(body)
            elif isinstance(body, str):
                self.fd.sendall(body.encode())
            elif isinstance(body, BufferedReader):
                self.fd.sendfile(body)
                body.close()

    def __str__(self):
        firstline = f"{self.method} {self.route} {self.version}"
        header = '\r\n'.join([f"{k}: {v}" for k, v in self.headers.items()])
        return f"{firstline}\r\n{header}\r\n\r\n{self.text()}"

    def __bytes__(self):
        firstline = f"{self.method} {self.route} {self.version}"
        header = '\r\n'.join([f"{k}: {v}" for k, v in self.headers.items()])
        return f"{firstline}\r\n{header}\r\n\r\n".encode() + self.body()


class App:

    def __init__(self, base_route="", base_handlers=None):
        self.base_route: str = f"/{base_route.strip().strip('/')}" if base_route else base_route
        self.base_handlers: list = list(base_handlers) if base_handlers else []
        self.head_match_routes: list = []
        self.parse_match_routes: list = []
        self.full_match_routes: dict = {}
        self.openapi_data: dict = {
            "paths": defaultdict(dict),
            "components": {
                "schemas": {},
            }
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
                    parameters = [
                        f"{parameter['name']}:{parameter['in']}"
                        for parameter in path["parameters"]
                    ]
                    for node in r.route_list:
                        if not node.name:
                            continue
                        if f"{node.name}:path" in parameters:
                            continue
                        path["parameters"].append({
                            "name": node.name,
                            "in": "path",
                            "required": True,
                        })
                    self.openapi_data["paths"][_route][_method.lower()] = path
                self.log.update({
                    "type": "parsermatch",
                    "route": _pretty_route(route),
                    "handlers": [handler.__name__ for handler in v],
                }).info(f"bind route")
            elif route.endswith("*"):
                match = route.strip().rstrip("/*").rstrip("*")
                self.head_match_routes.append((match, v))
                self.log.update({
                    "type": "headmatch",
                    "route": _pretty_route(route),
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
                    "route": _pretty_route(route),
                    "handlers": [handler.__name__ for handler in v],
                }).info(f"bind route")
        self.full_match_routes = routes
        self.running = True

    def party(self, route, *handlers) -> 'App':
        route = f"{self.base_route}/{route.strip().strip('/')}"
        if route not in self.full_match_routes:
            app = App(route, list(self.base_handlers) + list(handlers))
            app.data = self.data
            self.full_match_routes[route] = app
        return self.full_match_routes[route]

    def group(self, route, *handlers) -> 'App':
        return self.party(route, *handlers)

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

    def ins(self, obj):
        if type(obj) not in (type, FunctionType):
            return obj
        signature = inspect.signature(obj)
        parameters = signature.parameters
        if not parameters:
            return obj()
        args = []
        for parameter in parameters.values():
            if parameter.kind not in (parameter.POSITIONAL_OR_KEYWORD, parameter.POSITIONAL_ONLY):
                break
            if parameter.default is not parameter.empty:
                args.append(parameter.default)
                continue
            if parameter.annotation is parameter.empty:
                args.append(None)
                continue
            if getattr(parameter.annotation, "__module__", None) == "builtins":
                args.append(parameter.annotation())
                continue
            if parameter.annotation is App:
                args.append(self)
                continue
            args.append(self.ins(parameter.annotation))
        return obj(*args)

    def mount_apps(self, *modules):
        for modulename in modules:
            py_module = import_module(modulename)
            appname = getattr(py_module, "__app__", "App")
            mount_app = getattr(py_module, appname, None)
            self.ins(mount_app)

    def view(self, route, *handlers):
        if len(handlers) < 1:
            raise Exception("not found handlers")
        view = self.ins(handlers[-1])
        handlers = list(handlers[:-1])
        if hasattr(view, "use"):
            handlers += list(getattr(view, "use"))
        for method in ("get", "post", "head", "put", "delete", "patch", "options", "any"):
            method_handlers = handlers[:]
            if hasattr(view, f"http_{method}_use"):
                method_handlers += list(getattr(view, f"http_{method}_use"))
            if hasattr(view, f"http_{method}"):
                getattr(self, method)(route, *method_handlers, getattr(view, f"http_{method}"))

    def view_modules(
            self,
            module: str,
            *handlers,
            module_ignore_startswith=("_", "test_"),
            module_ignore_endswith=("_test"),
    ):
        if not re.match("[a-zA-Z0-9._]*", module):
            raise Exception("invalid module")
        stack = inspect.stack()
        caller_frame = stack[1]
        caller_module = inspect.getmodule(caller_frame[0])
        caller_module_dir = os.path.dirname(caller_module.__file__)
        caller_module_path = os.path.join(caller_module_dir, module.replace(".", os.sep))
        for filepath, _, files in os.walk(caller_module_path):
            base_module = os.path.basename(filepath)
            if base_module.startswith(module_ignore_startswith) or \
                    base_module.endswith(module_ignore_endswith):
                continue
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                child_module_name = os.path.splitext(filename)[0]
                child_module_path = ".".join(filter(None, [
                    caller_module.__package__,
                    os.path.relpath(filepath, caller_module_dir).replace(os.sep, ".")
                ]))
                child_module_route = os.path.relpath(filepath, caller_module_path).strip(".").replace(os.sep, "/")
                if child_module_name == "__init__":
                    child_module_name = ""
                    py_module = import_module(child_module_path)
                elif child_module_name.startswith(module_ignore_startswith):
                    continue
                elif child_module_name.endswith(module_ignore_endswith):
                    continue
                else:
                    py_module = import_module(child_module_path + "." + child_module_name)
                view_name = getattr(py_module, "__view__", "View")
                view_handler = getattr(py_module, view_name, None)
                if not view_handler:
                    self.log.update(package=py_module.__package__).warning(f"not found package `View Handler`")
                    continue
                view_route = getattr(py_module, "__route__", child_module_name).strip("/")
                if type(view_handler) is FunctionType:
                    view_handler(self.party(f"{child_module_route}/{view_route}", *handlers))
                    continue
                self.view(f"{child_module_route}/{view_route}", *handlers, view_handler)

    def openapi(
            self,
            enable=True,
            title="OpenAPI",
            description="Power By Pywss",
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
                "description": description,
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
                },
                "schemas": {},
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
        keepalive = True
        try:
            rfd = request.makefile("rb", -1)
            while keepalive:
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
                    keepalive = False
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
            log.debug("connect abort")
        except ConnectionResetError:
            log.debug("connect reset")
        except BrokenPipeError:
            log.debug("broken pipe")
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

    def watchdog(self, interval: float = float(os.environ.get("PYWSS_WATCHDOG_INTERVAL", 1))):
        log = self.log.update(role="watchdog")
        log.info("watching...")
        stat = {}
        allroutes = (self.full_match_routes.items(), self.parse_match_routes, self.head_match_routes)
        while self.running:
            module_detected = set()
            for routes in allroutes:
                for route, handlers in routes:
                    key = f"{route}"
                    handler = handlers[-1]
                    module = inspect.getmodule(handler)
                    if module.__name__ == "__main__":  # only restart
                        continue
                    sourcefile = inspect.getsourcefile(module)
                    mtime = int(os.path.getmtime(sourcefile))
                    if key not in stat:
                        stat[key] = mtime
                        continue
                    if stat[key] == mtime:
                        continue
                    stat[key] = mtime
                    try:
                        if module.__name__ not in module_detected:
                            module_detected.add(module.__name__)
                            log.update(module=module.__name__).info(f"detect module change")
                        if inspect.isfunction(handler):
                            handlers[-1] = getattr(reload(module), handler.__name__)
                        elif inspect.ismethod(handler):
                            cls = getattr(reload(module), handler.__self__.__class__.__name__)
                            handlers[-1] = getattr(self.ins(cls), handler.__name__)
                        else:
                            raise Exception(f"unsupport [{type(handler)}]")
                        log.update(route=key, module=module.__name__).info(f"update")
                    except:
                        log.traceback()
            time.sleep(interval)
        log.warning("exit")

    def fork_processes(self, num_processes: int):
        if sys.platform == "win32":
            raise Exception("fork not available on windows")
        pids = {}
        num_processes = num_processes if num_processes > 0 else os.cpu_count()
        for i in range(num_processes):
            pid = os.fork()
            if pid == 0:  # child process
                return pid
            else:
                pids[pid] = i
        # main process
        while pids:
            pid, status = os.wait()
            if pid not in pids:
                continue
            pids.pop(pid)
        return None

    def run(
            self,
            host: str = "0.0.0.0",
            port: int = int(os.environ.get("PYWSS_SERVER_PORT", 8080)),
            grace: int = int(os.environ.get("PYWSS_SERVER_GRACE", 0)),
            select_size: int = int(os.environ.get("PYWSS_SERVER_SELECT_SIZE", 5)),
            select_timeout: float = float(os.environ.get("PYWSS_SERVER_SELECT_TIMEOUT", 0.5)),
            thread_pool_size: int = int(os.environ.get("PYWSS_THREAD_POOL_SIZE", min(30, (os.cpu_count() or 1) * 5))),
            thread_pool_idle_time: int = int(os.environ.get("PYWSS_THREAD_POOL_IDLE_TIME", 300)),
            watch: bool = os.environ.get("PYWSS_WATCHDOG_ENABLE", "false").lower() == "true",
            fork: bool = False,
            num_processes: int = 0,
    ) -> None:
        # build app with [route:handler]
        self.build()
        # watchdog
        watch and threading.Thread(target=self.watchdog, daemon=True).start()
        # rigister signal closing
        for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGILL):
            signal.signal(sig, lambda *args: self.close())
        # use os.fork
        if fork:
            pid = self.fork_processes(num_processes)
            if pid is None:
                return
        # socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if fork:  # child
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind((host, port))
            sock.listen(select_size)
            # queue of threading pool
            QueueIns = getattr(queue, "SimpleQueue", None) or queue.Queue
            stat_queue = QueueIns()
            reqs_queue = QueueIns()
            thread_ident_pool = set()

            # worker of threading pool
            def thread_pool_worker():
                ident = threading.get_ident()
                log = self.log.update(thread=f"thread-{ident}")
                log.debug("use thread pool")
                while self.running:
                    try:
                        request, address = reqs_queue.get(block=True, timeout=thread_pool_idle_time)
                        self.handler_request(request, address)
                        stat_queue.get(block=False)
                    except queue.Empty:
                        break
                    except:
                        log.traceback()
                while self.running:
                    try:
                        thread_ident_pool.remove(ident)
                    except:
                        pass
                    if ident not in thread_ident_pool:
                        break
                log.warning(f"thread pool recycle - remain {len(thread_ident_pool)}")

            # selectors priority: epoll->poll->select
            selector = getattr(selectors, "EpollSelector", None) or \
                       getattr(selectors, "PollSelector", None) or \
                       selectors.SelectSelector
            with self.log.trycache():
                with selector() as _selector:
                    _selector.register(sock.fileno(), selectors.EVENT_READ)
                    self.log.update(
                        version=__version__,
                        host=host,
                        port=port,
                        ipaddress=get_ipaddress(),
                    ).info("server start")
                    while self.running:
                        ready = _selector.select(select_timeout)
                        if not ready:
                            continue
                        request, address = sock.accept()
                        current_stat_queue_size = stat_queue.qsize()
                        if current_stat_queue_size < thread_pool_size:
                            stat_queue.put(None)
                            reqs_queue.put((request, address))
                            current_stat_queue_size += 1
                            if current_stat_queue_size > len(thread_ident_pool):
                                t = threading.Thread(target=thread_pool_worker, daemon=True)
                                t.start()
                                thread_ident_pool.add(t.ident)
                        else:
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


class File:

    def __init__(self, name, filename, headers, content):
        self.name: str = name
        self.filename: str = filename
        self.content: bytes = content
        self.headers: dict = headers

    def __str__(self):
        return self.content.decode()


def once(func):
    def wrapper(*args, **kwargs):
        if wrapper.__done__:
            return True
        wrapper.__done__ = True
        return func(*args, **kwargs)

    wrapper.__done__ = False
    return wrapper


def get_ipaddress():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return None


def _pretty_route(route: str):
    if "/" not in route:
        return f"{route}:/"
    _method, _route = route.split("/", 1)
    return f"{_method}:/{_route}"
