import pywss

__view__ = "view"


def view(app: pywss.App):
    app.get("/", lambda ctx: ctx.write("test-view-func"))
