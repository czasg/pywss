# coding: utf-8
from .mysql import excute

def getAllUsers():
    return excute("SELECT * FROM users")
