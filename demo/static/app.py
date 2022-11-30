# coding: utf-8
import pywss


def main():
    app = pywss.App()
    app.static("/static", "./files")
    app.run()


if __name__ == '__main__':
    main()
