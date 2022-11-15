# coding: utf-8
from pywss import *


class AppLog(App):

    def _(self, request: socket.socket, address: tuple) -> None:
        log = self.log
        log.info("建立连接")
        try:
            keep_alive = True
            rfd = request.makefile("rb", -1)
            while keep_alive:
                method, path, version, err = parse_request_line(rfd)
                if err:
                    request.sendall(b"HTTP/1.1 400 BadRequest\r\n")
                    return
                log = log.update(method=method, path=path)
                hes, err = parse_headers(rfd)
                if err:
                    request.sendall(b"HTTP/1.1 400 BadRequest\r\n")
                    log.error(err)
                    return
                log.variables(method, path, version).info("获取请求")
                # check keep alive
                if hes.get("Connection", "").lower() == "close":
                    keep_alive = False
                    continue
                # full match
                paths = {}
                route = f"{method.upper()}/{path.split('?', 1)[0].strip('/')}"
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


if __name__ == '__main__':
    app = AppLog()
    app.static("/static", rootDir="./static")
    app.get("/", lambda ctx: ctx.redirect("/static/index.html"))
    app.run()
    """ 浏览器访问 ctrl+左键
    http://localhost:8080
    http://localhost:8080/static/index.html
    
    说明：
    - 首次访问，可以看到【建立连接】和【获取请求】的日志信息
    - 后续刷新页面，只会看到【获取请求】的日志信息
    """
