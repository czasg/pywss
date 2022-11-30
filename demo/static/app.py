# coding: utf-8
import pywss


def main():
    app = pywss.App()
    app.get("/", lambda ctx: ctx.redirect("/static/"))
    app.static("/static", ".")
    app.run()


if __name__ == '__main__':
    main()
