# coding: utf-8
import dao


def getUserList():
    users = []
    for user in dao.getUserList():
        users.append(dict(
            name=user.name,
            rid=user.role_id,
            createAt=user.create_at,
            updateAt=user.update_at,
        ))
    return users


def getUserInfo(uid: int):
    user = dao.getUserByID(uid)
    if not user:
        return None

    return dict(
        name=user.name,
        rid=user.role_id,
        createAt=user.create_at,
        updateAt=user.update_at,
        meta=user.meta,
    )
