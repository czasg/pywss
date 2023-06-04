import pywss


class View:

    def __init__(self, app: pywss.App):
        self.app = app

    def http_get(self, ctx: pywss.Context):
        ctx.write("test-view-app")
