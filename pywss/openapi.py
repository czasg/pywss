# coding: utf-8


# def transfer(object, properties=False):
#     resp = {}
#     if isinstance(object, dict):
#         for k, v in object.items():
#             description = None
#             if isinstance(v, tuple):
#                 v, description, = v
#             if not v:
#                 resp[k] = {
#                     "example": v
#                 }
#             elif isinstance(v, dict):
#                 resp[k] = transfer(v, True)
#             elif isinstance(v, list) and isinstance(v[0], tuple):
#                 v0, description, = v[0]
#                 resp[k] = {
#                     "items": transfer(v0, True)
#                 }
#             elif isinstance(v, list) and isinstance(v[0], (dict, list)):
#                 resp[k] = {
#                     "items": transfer(v[0], True),
#                 }
#             else:
#                 resp[k] = {
#                     "example": v
#                 }
#             if description:
#                 resp[k]["description"] = description
#         if properties:
#             return {"properties": resp}
#         return resp
#     elif isinstance(object, list):
#         # if isinstance(object[0], tuple):
#         #     object0, description = object
#         #     return {
#         #         "description": description,
#         #     }
#         if isinstance(object[0], list):
#             return {"items": transfer(object[0])}
#         if isinstance(object[0], dict):
#             return transfer(object[0], True)
#         return {"example": object}
#     return resp

def transfer(object):
    if isinstance(object, dict):
        return transfer_dict(object)
    if isinstance(object, list):
        return transfer_list(object)
    return {}


def transfer_dict(object: dict):
    data = {}
    for k, v in object.items():
        description = None
        if isinstance(v, tuple):
            v, description, = v
        if not v:
            data[k] = {
                "example": v
            }
        elif isinstance(v, dict):
            data[k] = transfer_dict(v)
        elif isinstance(v, list):
            data[k] = transfer_list(v)
        else:
            data[k] = {
                "example": v
            }
        if description:
            data[k]["description"] = description
    return {"properties": data}


def transfer_list(object: list):
    if not object:
        return {"example": object}
    if isinstance(object[0], tuple):
        object0, description, = object[0]
        items = transfer(object0)
        # if isinstance(items, dict):
        items["description"] = description
        return {"items": items}
    if isinstance(object[0], list):
        return {"items": transfer_list(object[0])}
    elif isinstance(object[0], dict):
        return {"items": transfer_dict(object[0])}
    else:
        return {"example": object}


def mid_split(param, split, default):
    params = param.split(split, 1)
    if len(params) == 1:
        return default
    return params[-1]


def docs(
        summary: str = None,
        description: str = None,
        tags: list = None,
        params: dict = None,
        request=None,
        response=None,
        responses: dict = None,
):
    if not responses:
        responses = {"200:desc:Response OK": response}
    path = {
        "summary": summary,
        "description": description,
        "tags": tags,
        "parameters": [
            {
                "name": param.split(":in:", 1)[0],
                "description": desc,
                "in": mid_split(param, ":in:", "query")
            }
            for param, desc in (params or {}).items()
        ],
        "_parameters_filter": {
            param if ":in:" in param else f"{param}:in:query": None
            for param in (params or {}).keys()
        },
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": transfer(request).pop("properties", {})
                    },
                }
            }
        },
        "responses": {
            f"{code.split(':desc:', 1)[0]}": {
                "description": mid_split(code, ":desc:", "No Response Description"),
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": transfer(resp).pop("properties", {})
                        },
                    }
                }
            }
            for code, resp in responses.items()
        }
    }

    def wrap(func):
        func.__openapi_path__ = path
        return func

    return wrap
