# coding: utf-8

def respOK(data, msg=""):
    return {
        "code": 10000,
        "msg": msg,
        "data": data,
    }


def respErr(msg, data):
    return {
        "code": 99999,
        "msg": msg,
        "data": data,
    }
