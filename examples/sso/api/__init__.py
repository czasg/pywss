# coding: utf-8
from middleware.just_admin import justAdmin


def registerAPI(app):
    app.post("/user/login")
    app.post("/user/logout")

    app.post("/user/auth")

    app.get("/user/info")

    app.get("/user/list", justAdmin)
