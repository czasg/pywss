# coding: utf-8
def transfer(object) -> dict:
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
        items["description"] = description
        return {"items": items}
    if isinstance(object[0], list):
        return {"items": transfer_list(object[0])}
    elif isinstance(object[0], dict):
        return {"items": transfer_dict(object[0])}
    else:
        return {"example": object}


def get_object_content_type(object):
    if isinstance(object, (dict, list)):
        return "application/json"
    return "application/octet-stream"


def get_object_type(object):
    if isinstance(object, dict):
        return "object"
    if isinstance(object, list):
        return "array"
    return "string"


def get_schema(object):
    resp = transfer(object)
    resp["type"] = get_object_type(object)
    return resp


def get_parameters(object):
    if not object:
        return []
    resp = []
    for param, desc in object.items():
        params = {
            "name": param,
            "description": desc,
            "in": "query",
            "required": False
        }
        if ":" not in param:
            resp.append(params)
            continue
        pars = param.split(":", 1)
        params["name"] = pars[0]
        for par in pars[1].split(","):
            if par in ("query", "header", "path", "cookie"):
                params["in"] = par
            elif par == "required":
                params["required"] = True
        resp.append(params)
    return resp


def parameters_filter(path, object):
    if not object:
        return False
    for param in object:
        if param["name"] == path and param["in"] == "path":
            return True
    return False


def docs(
        summary: str = None,
        description: str = None,
        tags: list = None,
        params: dict = None,
        request: dict or str = None,
        request_type: str = None,
        response: dict or list or str = None,
        responses_type: str = None,
        responses: dict = None,
):
    if not responses:
        responses = {"200:Response OK": response}
    path = {
        "summary": summary,
        "description": description,
        "tags": tags,
        "parameters": get_parameters(params),
        "requestBody": {
            "content": {
                request_type or get_object_content_type(request): {
                    "schema": get_schema(request),
                }
            }
        },
        "responses": {
            f"{code.split(':', 1)[0]}": {
                "description": code[code.index(':') + 1:] if ":" in code else "No Response Description",
                "content": {
                    responses_type or get_object_content_type(resp): {
                        "schema": get_schema(resp),
                    }
                }
            }
            for code, resp in responses.items()
        },
        "security": [
            {
                "bearerAuth": [],
            },
            {
                "basicAuth": [],
            },
            {
                "ApiKeyAuth": [],
            },
        ]
    }

    def wrap(func):
        func.__openapi_path__ = path
        return func

    return wrap


def merge_dict(dict1: dict, dict2: dict):
    resp = {}
    for k, v in dict1.items():
        if k not in dict2:
            resp[k] = v
            continue
        if isinstance(v, dict) and isinstance(dict2[k], dict):
            resp[k] = merge_dict(v, dict2[k])
            continue
        resp[k] = v
    for k, v in dict2.items():
        if k not in dict1:
            resp[k] = v
            continue
        if isinstance(v, dict) and isinstance(dict1[k], dict):
            resp[k] = merge_dict(v, dict1[k])
            continue
    return resp


def openapi_ui_template(
        title,
        openapi_json,
        openapi_ui_js_url,
        openapi_ui_css_url,
):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{openapi_ui_css_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{openapi_ui_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_json}',
        dom_id: '#swagger-ui',
        layout: 'BaseLayout',
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
        }})
    </script>
        </body>
        </html>
    """
