# coding: utf-8
import cc
import pywss
import loggus
import webbrowser


class ServerCommand(cc.Command):
    class flags:
        host = cc.FlagStr(flags=["--host"], description="web server host", default="0.0.0.0")
        port = cc.FlagInt(flags=["-p", "--port"], description="web server port", default=8080)
        default_route = cc.FlagStr(flags=["--default-route"],
                                   description="default route if not specified",
                                   default="/")
        default_code = cc.FlagInt(flags=["--default-code"],
                                  description="default response code if not specified",
                                  default=200)
        default_body = cc.FlagStr(flags=["--default-body"],
                                  description="efault response body if not specified")
        route = cc.FlagList(flags=["-r", "--route"],
                            description='method:route:code:body\n'
                                        'eg: [--route="GET:/hello:200:hello,pywss"]')
        static = cc.FlagList(flags=["--static"],
                             description='localDir:staticRoute\n'
                                         'eg: [--static="/localDir:/staticRoute"]')
        log_level = cc.FlagStr(flags=["--log-level"],
                               description="log level for loggus",
                               default="INFO")
        web = cc.FlagBool(flags=["--web"], description="open browser with `--static`")
        debug = cc.FlagBool(flags=["-d", "--debug"],
                            description="don't start server, just debug pywss.")

    def descriptions(self) -> str:
        return """
        Web Server By Pywss
        """

    def run(self, *args, **flags):
        flags = cc.Flag.parse_value(self.flags)
        app = pywss.App()
        app.log.SetLevel(getattr(loggus, flags.log_level))
        try:
            app.any(
                flags.default_route,
                lambda ctx: print(ctx) or ctx.next(),
                lambda ctx: ctx.set_status_code(flags.default_code) or ctx.next(),
                lambda ctx: ctx.write(flags.default_body) or ctx.next(),
            )
            for arg in flags.route:
                method, route, code, body = arg.split(":", 3)
                getattr(app, method.lower())(route, handler_wrap(int(code), body))
            for arg in flags.static:
                rootDir, route = arg.split(":", 1)
                app.static(route, rootDir=rootDir)
            if not flags.debug and flags.static and flags.web:
                _, route = flags.static[0].split(":", 1)
                webbrowser.open(f"http://localhost:{flags.port}/{route.strip('/')}")
        except:
            app.log.traceback()
            self.help(1)
        if flags.debug:
            app.build()
            app.log.info("debug - not run server")
            return
        app.run(host=flags.host, port=flags.port)


def handler_wrap(code: int, body: str):
    def handler(ctx: pywss.Context):
        ctx.set_status_code(code)
        ctx.write(body)

    return handler
