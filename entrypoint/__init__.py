# coding: utf-8
import pywss
import loggus
import argparse


def new_handler(code: int, body: str):
    def handler(ctx: pywss.Context):
        ctx.set_status_code(code)
        ctx.write(body)

    return handler


def main():
    parser = argparse.ArgumentParser(
        prog="pywss",
        description="CMD Web Server By Pywss"
    )
    parser.add_argument("--host", default='0.0.0.0',
                        help="web server host, default[0.0.0.0]")
    parser.add_argument("--port", default=8080, type=int,
                        help="web server port, default[8080]")
    parser.add_argument("--route", action='append', default=[],
                        help='method:route:code:body, eg[--route="GET:/hello:200:hello,world"]')
    parser.add_argument("--static", action='append', default=[],
                        help='eg[--static="/localDir:/staticRoute"]')
    parser.add_argument("--restart", choices=['always', 'never'],
                        help='todo')
    parser.add_argument("--log-level", choices=['debug', 'info', 'warn', 'error', 'panic'],
                        help='todo')
    args = parser.parse_args()

    with loggus.trycache():
        app = pywss.App()
        for arg in args.route or ['GET:/:200:Hello Pywss']:
            method, route, code, body = arg.split(":", 3)
            getattr(app, method.lower())(route, new_handler(int(code), body))
        for arg in args.static:
            rootDir, route = arg.split(":", 1)
            app.static(route, rootDir=rootDir)
        app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
