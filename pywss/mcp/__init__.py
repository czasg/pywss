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
                 mcp_endpoint="mcp", sse_endpoint="sse", message_endpoint="message"):
        self.name = name
        self.version = version
        self.lock = threading.Lock()
        self.mcp_endpoint = mcp_endpoint
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
        # use handler
        def session_handler(ctx: pywss.Context):
            ctx.data.session_id = ctx.query.get("session_id") or ctx.query.get("session")
            ctx.next()

        app.use(session_handler)

        # sse transport
        app.get(self.sse_endpoint, self.handle_sse)
        app.post(self.message_endpoint, self.handle_message)

        # http stream transport
        app.get(self.mcp_endpoint, self.handle_sse)
        app.post(self.mcp_endpoint, self.handle_mcp_post)
        app.delete(self.mcp_endpoint, self.handle_mcp_delete)
        app.options(self.mcp_endpoint, lambda ctx: ctx.next())  # use cors before mount

        # http api pure
        for tool in self.tools:
            self.register_http_handler(app, tool)
        app.get("/tools", self.handle_tools)

    def register_http_handler(self, app, tool):
        handler = getattr(self, f"tool_{tool.name}")
        baseModel = handler.__openapi_request__
        if not baseModel:
            loggus.panic(f"tool[{tool.name}] must be register by `@pywss.openapi.docs`")

        def request_handler(ctx: pywss.Context):
            try:
                ctx.data.req = handler.req_cls.model_validate(ctx.json())
            except Exception as e:
                self.handle_error(ctx, PARSE_ERROR, f"Parse Error: {e}")
            else:
                ctx.next()

        app.post(f"/tools/{tool.name}", request_handler, handler)

    @pywss.openapi.docs()
    def handle_tools(self, ctx: pywss.Context):
        ctx.write_json(self.tools, cls=CustomJSONEncoder)

    def handle_sse(self, ctx: pywss.Context):
        session_id = ctx.data.session_id
        if not session_id:
            session_id = str(uuid.uuid4())
            ctx.sse_event(self.message_endpoint + f"?session_id={session_id}", "endpoint")

        q = queue.Queue()
        with self.lock:
            self.queueMap[session_id] = q

        log = ctx.log.update(session_id=session_id)
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
            del self.queueMap[session_id]
            log.info(f"session closed")

    def handle_mcp_post(self, ctx: pywss.Context):
        # parse session id
        session_id = ctx.data.session_id
        if not session_id:
            ctx.data.session_id = str(uuid.uuid4())
        ctx.set_header("Mcp-Session-Id", ctx.data.session_id)

        # handle message
        self.handle_message(ctx)

    def handle_mcp_delete(self, ctx: pywss.Context):
        # parse session id
        session_id = ctx.data.session_id
        if not session_id:
            return

    def handle_message(self, ctx: pywss.Context):
        # parse base_message
        base_message = ctx.json()
        ctx.data.message_id = base_message.get("id")
        log = ctx.log.update(message_id=ctx.data.message_id)

        # parse session id
        session_id = ctx.data.session_id
        if not session_id:
            self.handle_error(ctx, INVALID_REQUEST, "Invalid Request")
            return
        log = log.update(session_id=session_id)

        # parse jsonrpc
        if base_message.get("jsonrpc", None) != "2.0":
            self.handle_error(ctx, INVALID_REQUEST, "Invalid Request")
            return

        # handle result
        if base_message.get("result"):
            log.info("result received")
            return

        # handle notification
        if base_message.get("id", None) is None:
            log.info(f"notification received")
            return

        # parse method
        method = base_message.get("method")
        ctx.data.method = method
        log = log.update(method=method)

        # handle message by method
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
                self.handle_error(ctx, METHOD_NOT_FOUND, f"tool {tool_name} not found")
                return
            try:
                ctx.data.req = tools[0].req_cls.model_validate(arguments)
            except Exception as e:
                self.handle_error(ctx, PARSE_ERROR, f"parse error: {e}")
            else:
                tool_call = getattr(self, f"tool_{tool_name}")
                tool_call(ctx)
                log.info("tool call received")
        else:
            self.handle_error(ctx, METHOD_NOT_FOUND, f"method {method} not supported")

    def handle_success(self, ctx: pywss.Context, result):
        if ctx.data.method == MethodToolsCall:
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
            "id": ctx.data.message_id,
            "jsonrpc": "2.0",
            "result": result
        }
        ret = json.dumps(ret, ensure_ascii=False, cls=CustomJSONEncoder)
        ctx.write_json(ret)
        q = self.queueMap.get(ctx.data.session_id)
        if q:
            q.put(ret)

    def handle_error(self, ctx: pywss.Context, code: int = INTERNAL_ERROR, message: str = "INTERNAL ERROR"):
        ret = {
            "id": ctx.data.message_id,
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            }
        }
        ret = json.dumps(ret, ensure_ascii=False, cls=CustomJSONEncoder)
        ctx.write_json(ret)
        q = self.queueMap.get(ctx.data.session_id)
        if q:
            q.put(ret)
