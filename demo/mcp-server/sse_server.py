# coding: utf-8
import pywss
from enum import Enum
from pydantic import BaseModel
from pywss.mcp import MCPServer


class Color(str, Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class DomainReq(BaseModel):
    domain: str
    color: Color


class DomainsReq(BaseModel):
    domains: list[str]


class DomainMCPServer(MCPServer):

    @pywss.openapi.docs(description="获取单个域名服务", request=DomainReq)  # required
    def tool_get_domain(self, ctx: pywss.Context):
        req: DomainReq = ctx.data.req
        self.handle_success(ctx, {
            "domain": req.domain,
            "color": req.color
        })

    @pywss.openapi.docs(description="获取批量域名服务", request=DomainsReq)  # required
    def tool_get_domains(self, ctx: pywss.Context):
        req: DomainsReq = ctx.data.req
        self.handle_success(ctx, {
            "domains": req.domains,
        })

    @pywss.openapi.docs(description="获取http域名服务", request=DomainsReq)  # required
    def tool_http_get_domains(self, ctx: pywss.Context):
        print(ctx)

    def notification_initialized(self, ctx: pywss.Context):
        print("notification_initialized")
        print(ctx)


mcpServer = DomainMCPServer()

app = pywss.App()
app.openapi()
mcpServer.mount(app.party("/api/v1/mcp"))
app.run()
