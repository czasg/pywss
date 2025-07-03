# coding: utf-8
import json

from pydantic import BaseModel
from pywss.utils import safe_encoder, resolve_refs


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
        responses = {"200": response}
    path = {
        "summary": summary,
        "description": description,
        "tags": tags,
        "parameters": transfer_parameters(params),
        "requestBody": {
            "content": transfer_schema(request, request_type),
        },
        "responses": {
            f"{code}": {
                "content": transfer_schema(resp, responses_type),
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
        func.__openapi_path__ = json.loads(json.dumps(path, default=safe_encoder))
        if issubclass(request, BaseModel):
            func.__openapi_request__ = request
        return func

    return wrap


def transfer_parameters(object: dict):
    params = []
    for key, desc in (object or {}).items():
        param = {
            "name": key,
            "description": desc,
            "in": "query",
            "required": False
        }
        if ":" not in key:
            params.append(param)
            continue
        keys = key.split(":", 1)
        param["name"] = keys[0]
        for par in keys[1].split(","):
            if par in ("query", "header", "path", "cookie"):
                param["in"] = par
            elif par == "required":
                param["required"] = True
        params.append(param)
    return params


def transfer_content_type(object):
    return ({
        dict: "application/json",
        list: "application/json",
        str: "text/html"
    }).get(type(object), "application/octet-stream")


def transfer_schema(object, objectType):
    if isinstance(object, BaseModel) or issubclass(object, BaseModel):
        schema = object.model_json_schema()
        definitions = schema.pop("$defs", {})
        return {
            "application/json": {
                "schema": resolve_refs(schema, definitions)
            }
        }
    if hasattr(object, "__fields__"):
        object = transfer_fields(object)
    return {
        objectType or transfer_content_type(object): {
            "schema": {
                "example": object
            }
        }
    }


def transfer_fields(object):
    return {
        key: filed.default or ({
            str: "string",
            int: "integer",
            list: "array",
            dict: "object",
            bool: "boolean",
        }).get(filed.type_, "string")
        for key, filed in object.__fields__.items()
    }


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
