import pywss


class View:

    def http_get(self, ctx: pywss.Context):
        ctx.write("test")
