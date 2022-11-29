# coding: utf-8
import pywss
import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="pywss",
        description="CMD Web Server By Pywss"
    )
    parser.add_argument("--host", default='0.0.0.0',
                        help="web server host, default[0.0.0.0]")
    parser.add_argument("--port", default=8080, type=int,
                        help="web server port, default[8080]")
    parser.add_argument("--route", action='append', default=['GET:/:200:Hello Pywss'],
                        help='method:route:code:body, eg[--route="GET:/hello:200:hello,world"]')
    parser.add_argument("--static", action='append', default=[],
                        help='eg[--static="/localDir:/staticRoute"]')
    parser.add_argument("--restart", choices=['always', 'never'],
                        help='todo')
    parser.add_argument("--log-level", choices=['debug', 'info', 'warn', 'error', 'panic'],
                        help='todo')
    args = parser.parse_args()

    app = pywss.App()
    with app.log.trycache():
        for arg in args.route:
            method, route, code, body = arg.split(":", 3)
            getattr(app, method.lower())(route, lambda ctx: (ctx.set_status_code(int(code)) or ctx.write(body)))
        for arg in args.static:
            rootDir, route = arg.split(":", 1)
            app.static(route, rootDir=rootDir)
        app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
