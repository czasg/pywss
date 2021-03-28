# coding: utf-8
import time

from typing import List
from .database import DB, User


def getAllUsers() -> List[User]:
    cursor = DB.cursor()
    cursor.execute("SELECT * FROM user")
    users = [User(**user) for user in cursor.fetchall()]  # type: List[User]
    cursor.close()
    return users


def getUserByID(id: int) -> User:
    cursor = DB.cursor()
    cursor.execute(f"SELECT * FROM user WHERE `id` = {id}")
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(**user)
    return None


def getUserByName(name: str) -> User:
    cursor = DB.cursor()
    cursor.execute(f"SELECT * FROM user WHERE name = '{name}'")
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(**user)
    return None


def addUser(name, pwd, email) -> User:
    now = int(time.time())
    cursor = DB.cursor()
    cursor.execute(f"INSERT INTO user (`name`, `password`, `email`, `create_at`, `update_at`, `login_at`) "
                   f"VALUES ('{name}', '{pwd}', '{email}', {now}, {now}, {now})")
    DB.commit()
    cursor.close()


def delUserByID(id: int) -> User:
    pass


def updateUser() -> User:
    pass
