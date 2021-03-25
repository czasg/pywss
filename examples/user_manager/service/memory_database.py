# coding: utf-8
import threading
from collections import Counter

lock = threading.Lock()


def newId():
    uniqueId = 1
    while True:
        yield uniqueId
        lock.acquire()
        uniqueId += 1
        lock.release()


class User:
    Id: int
    Name: str
    Age: int
    Email: str
    Salary: int

    def __init__(self):
        pass


class FakeUserDao:

    def __init__(self):
        self.users = []

    def getUsers(self):
        return self.users

    def getUserById(self, userId):
        for user in self.users:
            pass


userDao = FakeUserDao()
