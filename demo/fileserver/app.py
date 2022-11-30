# coding: utf-8
import pywss


def main():
    app = pywss.App()
    app.get("/", lambda ctx: ctx.redirect("/file-server/"))
    app.static("/file-server", ".")
    app.run()


if __name__ == '__main__':
    main()
