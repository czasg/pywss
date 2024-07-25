# coding: utf-8
import json

from typing import Any
from copy import deepcopy


def split_method_route(string):
    if "/" not in string:
        return string, "/"
    method, route = string.split("/", 1)
    return method, "/" + route.strip("/")


def safe_encoder(obj):
    try:
        return json.dumps(obj)
    except:
        return str(obj)


def merge_dict(dict1: dict, dict2: dict):
    obj = deepcopy(dict1)
    for k, v in dict2.items():
        if k not in obj:
            obj[k] = v
            continue
        if isinstance(obj[k], dict) and isinstance(v, dict):
            obj[k] = merge_dict(obj[k], v)
    return obj


class Query(dict):

    def fetch(self, *args, typ: Any = str):
        ret = [typ()] * len(args)
        for index, arg in enumerate(args):
            if arg in self:
                ret[index] = typ(self[arg])
        return ret
