# coding: utf-8
import pywss
import loggus
import argparse
import webbrowser


def handler_wrap(code: int, body: str):
    def handler(ctx: pywss.Context):
        ctx.set_status_code(code)
        ctx.write(body)

    return handler


def main(args=None):
    parser = argparse.ArgumentParser(
        prog="pywss",
        description="CMD Web Server By Pywss"
    )
    parser.add_argument("--host", default='0.0.0.0', type=str,
                        help="web server host, default[0.0.0.0]")
    parser.add_argument("--port", default=8080, type=int,
                        help="web server port, default[8080]")
    parser.add_argument("--route", action='append', default=[],
                        help='method:route:code:body, eg[--route="GET:/hello:200:hello,pywss"]')
    parser.add_argument("--static", action='append', default=[],
                        help='eg[--static="/localDir:/staticRoute"]')
    parser.add_argument("--restart", choices=['always', 'never'],
                        help='todo')
    parser.add_argument("--log-level", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'PANIC'], default="INFO",
                        help='log level for loggus')
    parser.add_argument("--web", action='store_const', const=True,
                        help='open browser with `--static`')
    parser.add_argument("--debug", action='store_const', const=True,
                        help='not run server')
    args = parser.parse_args(args)

    app = pywss.App()
    app.log.SetLevel(getattr(loggus, args.log_level))
    try:
        for arg in args.route:
            method, route, code, body = arg.split(":", 3)
            getattr(app, method.lower())(route, handler_wrap(int(code), body))
        for arg in args.static:
            rootDir, route = arg.split(":", 1)
            app.static(route, rootDir=rootDir)
        if not args.debug and args.static and args.web:
            _, route = args.static[0].split(":", 1)
            webbrowser.open(f"http://localhost:{args.port}/{route.strip('/')}")
        if not args.route and not args.static:
            app.get("/", lambda ctx: ctx.write("hello, pywss"))
    except:
        app.log.traceback()
        print("---help---")
        parser.print_help()
        return
    if args.debug:
        app.log.info("debug - not run server")
        return
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main(["--debug"])
