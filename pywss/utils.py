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

    def fetch(self, *args):
        ret = [None] * len(args)
        for index, arg in enumerate(args):
            if arg in self:
                ret[index] = self[arg]
        if len(ret) == 1:
            return ret[0]
        return ret


def resolve_refs(schema, definitions):
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref = schema["$ref"].split("/")[-1]
            return resolve_refs(definitions[ref], definitions)
        return {k: resolve_refs(v, definitions) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [resolve_refs(item, definitions) for item in schema]
    else:
        return schema
