# coding: utf-8


def transfer(object):
    if not object:
        return {}
    if isinstance(object, dict):
        resp = {}
        for k, v in object.items():
            description = None
            if isinstance(v, tuple):
                v, description, = v
            if isinstance(v, dict):
                resp[k] = {
                    "properties": transfer(v),
                }
            elif isinstance(v, list) and v and isinstance(v[0], (dict, list)):
                if isinstance(v[0], dict):
                    resp[k] = {
                        "items": {
                            "properties": transfer(v[0])
                        },
                    }
                if isinstance(v[0], list):
                    resp[k] = {
                        "items": transfer(v[0]),
                    }
            else:
                resp[k] = {
                    "example": v,
                }
            if description:
                resp[k]["description"] = description
        return resp
    if isinstance(object, list):
        if isinstance(object[0], list):
            return {"items": transfer(object[0])}
        if isinstance(object[0], dict):
            return {"properties": transfer(object[0])}
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
                        "properties": transfer(request)
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
                            "properties": transfer(resp)
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
