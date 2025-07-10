# coding: utf-8
import pywss
import uuid
import json
import queue
import loggus
import threading
from pydantic import BaseModel

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

MethodInitialize = "initialize"
MethodPing = "ping"
MethodToolsList = "tools/list"
MethodToolsCall = "tools/call"


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_json"):
            return obj.to_json()
        if hasattr(obj, "__json__"):
            return obj.__json__()
        return super().default(obj)


class MCPTool:
    def __init__(self, name, description, req_cls: BaseModel):
        self.name = name
        self.description = description
        schema = req_cls.model_json_schema()
        definitions = schema.pop("$defs", {})
        self.schema = pywss.utils.resolve_refs(schema, definitions)
        self.req_cls = req_cls

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.schema
        }


class MCPServer:

    def __init__(self, name="pywss-mcp-server", version=pywss.__version__,
                 sse_endpoint="sse", message_endpoint="message"):
        self.name = name
        self.version = version
        self.lock = threading.Lock()
        self.sse_endpoint = sse_endpoint
        self.message_endpoint = message_endpoint
        self.queueMap = {}
        # init mcp tools
        self.init_tools()

    def init_tools(self):
        self.tools = []
        for attr in dir(self):
            if attr.startswith("tool_") and callable(getattr(self, attr)):
                tool_name = attr[5:]
                tool_call = getattr(self, attr)
                if not hasattr(tool_call, "__openapi_request__"):
                    loggus.panic(f"tool[{tool_name}] must be register by `@pywss.openapi.docs`")
                description = tool_call.__openapi_path__["description"]
                request_cls = tool_call.__openapi_request__
                self.tools.append(MCPTool(tool_name, description, request_cls))
        self.tools.sort(key=lambda x: x.name)

    def mount(self, app: pywss.App):
        app.get(self.sse_endpoint, self.handle_sse)
        app.post(self.message_endpoint, self.handle_message)

        for tool in self.tools:
            handler = getattr(self, f"tool_{tool.name}")
            app.post(f"/tools/{tool.name}", self.register_http_handler(handler), handler)
        app.get("/tools", self.handler_tools)

    def register_http_handler(self, tool):
        baseModel = tool.__openapi_request__
        if not baseModel:
            loggus.panic(f"tool[{tool.name}] must be register by `@pywss.openapi.docs`")

        def handler(ctx: pywss.Context):
            try:
                ctx.data.req = baseModel.model_validate(ctx.json())
            except Exception as e:
                self.handle_error(ctx, PARSE_ERROR, f"Parse Error: {e}")
            else:
                ctx.next()

        return handler

    @pywss.openapi.docs()
    def handler_tools(self, ctx: pywss.Context):
        ctx.write_json(self.tools, cls=CustomJSONEncoder)

    def handle_sse(self, ctx: pywss.Context):
        uid = str(uuid.uuid4())
        q = queue.Queue()
        with self.lock:
            self.queueMap[uid] = q
        ctx.sse_event(self.message_endpoint + f"?session_id={uid}", "endpoint")
        log = ctx.log.update(session_id=uid)
        log.info(f"sse session opened")
        tolerance = 30
        while not ctx.is_closed():
            try:
                message = q.get(timeout=10)
                if message:
                    ctx.sse_event(message)
                    tolerance = 30
            except queue.Empty:
                tolerance -= 1
                if tolerance <= 0:
                    log.warning(f"session tolerance reached")
                    break
            except:
                loggus.traceback()
                break
        with self.lock:
            del self.queueMap[uid]
            log.info(f"session closed")

    def handle_message(self, ctx: pywss.Context):
        uid = ctx.query.get("session_id")
        if not uid:
            self.handle_error(ctx, INVALID_REQUEST, "Invalid Request")
            return
        log = ctx.log.update(session_id=uid)
        base_message = ctx.json()
        if base_message.get("id", None) is None:
            # handle notification
            log.info(f"notification received")
            return
        method = base_message.get("method")
        log = log.update(method=method)
        ctx.data.method = method
        if base_message.get("jsonrpc", None) != "2.0":
            self.handle_error(ctx, INVALID_REQUEST, "Invalid Request")
            return
        if base_message.get("result"):
            log.info("result received")
            return
        if method == MethodInitialize:
            params = base_message.get("params", {})
            params["serverInfo"] = {"name": self.name, "version": self.version}
            self.handle_success(ctx, params)
            log.info("initialize received")
        elif method == MethodPing:
            self.handle_success(ctx, {})
            log.info("ping received")
        elif method == MethodToolsList:
            self.handle_success(ctx, {"tools": self.tools})
            log.info("tools list received")
        elif method == MethodToolsCall:
            params = base_message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            tools = [tool for tool in self.tools if tool.name == tool_name]
            if not tools:
                self.handle_error(ctx, METHOD_NOT_FOUND, f"Tool {tool_name} not found")
                return
            try:
                ctx.data.req = tools[0].req_cls.model_validate(arguments)
            except Exception as e:
                self.handle_error(ctx, PARSE_ERROR, f"Parse Error: {e}")
            else:
                tool_call = getattr(self, f"tool_{tool_name}")
                tool_call(ctx)
                log.info("tool call received")
        else:
            self.handle_error(ctx, METHOD_NOT_FOUND, f"Method {method} not found")

    def handle_success(self, ctx: pywss.Context, result):
        uid = ctx.query.get("session_id")
        q = self.queueMap.get(uid)
        if not q:
            ctx.write(result)
            return
        method = ctx.data.method
        if method == MethodToolsCall:
            if not isinstance(result, str):
                result = json.dumps(result, ensure_ascii=False, cls=CustomJSONEncoder)
            result = {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        ret = {
            "id": ctx.json().get("id"),
            "jsonrpc": "2.0",
            "result": result
        }
        ret = json.dumps(ret, ensure_ascii=False, cls=CustomJSONEncoder)
        q.put(ret)
        ctx.write_json(ret)

    def handle_error(self, ctx: pywss.Context, code: int, message: str):
        uid = ctx.query.get("session_id")
        q = self.queueMap.get(uid)
        if not q:
            ctx.write({"code": code, "message": message})
            return
        ret = {
            "id": ctx.json().get("id"),
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        ret = json.dumps(ret, ensure_ascii=False, cls=CustomJSONEncoder)
        q.put(ret)
        ctx.write_json(ret)
