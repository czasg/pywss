# coding: utf-8
import json
import pywss
import unittest
import pywss.mcp
from pydantic import BaseModel


class TraceReq(BaseModel):
    traceId: str


class LogMCPServer(pywss.mcp.MCPServer):

    @pywss.openapi.docs(description="test", request=TraceReq)
    def tool_get_log(self, ctx: pywss.Context):
        req: TraceReq = ctx.data.req
        self.handle_success(ctx, {"traceId": req.traceId})


class TestBase(unittest.TestCase):

    def test_mcp_sse(self):
        app = pywss.App()

        LogMCPServer().mount(app.group("/api/v1/log"))

        req = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "initialize"
        }
        resp = pywss.HttpTestRequest(app).post("/api/v1/log/message", json=req)
        data = json.loads(resp.body)
        self.assertEqual(data, {'error': {'code': -32600, 'message': 'Invalid Request Without Session'},
                                'id': 1,
                                'jsonrpc': '2.0'})

    def test_mcp_stream_http(self):
        app = pywss.App()

        LogMCPServer(mcp_endpoint="mcpo").mount(app.group("/api/v1/log"))

        initialize_req = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "initialize"
        }
        resp = pywss.HttpTestRequest(app).post("/api/v1/log/mcpo", json=initialize_req)
        initialize_ret = json.loads(resp.body)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertIn("Mcp-Session-Id", resp.headers)
        self.assertIn("id", initialize_ret)
        self.assertIn("jsonrpc", initialize_ret)
        self.assertIn("result", initialize_ret)

        tool_list_req = {
            "id": 2,
            "jsonrpc": "2.0",
            "method": "tools/list"
        }
        resp = pywss.HttpTestRequest(app).post("/api/v1/log/mcpo", json=tool_list_req)
        tool_list_ret = json.loads(resp.body)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertIn("Mcp-Session-Id", resp.headers)
        self.assertIn("id", tool_list_ret)
        self.assertIn("jsonrpc", tool_list_ret)
        self.assertIn("result", tool_list_ret)
        self.assertEqual(tool_list_ret, {
            'id': 2,
            'jsonrpc': '2.0',
            'result': {'tools':
                [
                    {'description': 'test',
                     'inputSchema': {
                         'properties': {'traceId': {'title': 'Traceid',
                                                    'type': 'string'}},
                         'required': ['traceId'],
                         'title': 'TraceReq',
                         'type': 'object'},
                     'name': 'get_log'
                     }
                ]
            }
        })

        tool_call_req = {
            "id": 3,
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "log",
                "arguments": {
                    "traceId": "tool not found"
                }
            }
        }
        resp = pywss.HttpTestRequest(app).post("/api/v1/log/mcpo", json=tool_call_req)
        tool_call_ret = json.loads(resp.body)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertIn("Mcp-Session-Id", resp.headers)
        self.assertIn("id", tool_call_ret)
        self.assertIn("jsonrpc", tool_call_ret)
        self.assertIn("error", tool_call_ret)
        self.assertEqual(tool_call_ret,
                         {'id': 3, 'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'tool log not found'}})

        tool_call_req = {
            "id": 4,
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_log",
                "arguments": {
                    "traceId": "123456"
                }
            }
        }
        resp = pywss.HttpTestRequest(app).post("/api/v1/log/mcpo", json=tool_call_req)
        tool_call_ret = json.loads(resp.body)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Content-Type"), "application/json")
        self.assertIn("Mcp-Session-Id", resp.headers)
        self.assertIn("id", tool_call_ret)
        self.assertIn("jsonrpc", tool_call_ret)
        self.assertIn("result", tool_call_ret)
        self.assertEqual(tool_call_ret,
                         {'id': 4,
                          'jsonrpc': '2.0',
                          'result': {'content': [{'text': '{"traceId": "123456"}', 'type': 'text'}]}})

        req = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "initialize"
        }
        resp = pywss.HttpTestRequest(app).post("/api/v1/log/message", json=req)
        data = json.loads(resp.body)
        self.assertEqual(data, {'error': {'code': -32600, 'message': 'Invalid Request Without Session'},
                                'id': 1,
                                'jsonrpc': '2.0'})

    def test_mcpo(self):
        app = pywss.App()

        LogMCPServer().mount(app.group("/api/v1/log"))

        resp = pywss.HttpTestRequest(app).post("/api/v1/log/tools/get_log", json={"traceId": "123456"})
        ret = json.loads(resp.body)
        self.assertEqual(ret, {'id': None, 'jsonrpc': '2.0', 'result': {'traceId': '123456'}})

        resp = pywss.HttpTestRequest(app).post("/api/v1/log/tools/get_log_not_found", json={"traceId": "123456"})
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
