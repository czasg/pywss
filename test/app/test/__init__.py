import pywss


def App(app: pywss.App):
    app.get("/test", lambda ctx: ctx.write("test"))
