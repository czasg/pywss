# coding: utf-8
from pywss.ctx import Ctx
from service.user import getUserList as sGetUserList


def getUserList(ctx: Ctx):
    users = []
    for user in sGetUserList():
        users.append(dict(name=user.name, rid=user.role_id, createAt=user.create_at, updateAt=user.update_at,
                          loginAt=user.login_at))
    ctx.write(users)
