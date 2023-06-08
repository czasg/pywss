"use strict";(self.webpackChunkpywss_docs=self.webpackChunkpywss_docs||[]).push([[293],{3905:(e,t,n)=>{n.d(t,{Zo:()=>c,kt:()=>y});var r=n(7294);function s(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function l(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){s(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,r,s=function(e,t){if(null==e)return{};var n,r,s={},a=Object.keys(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||(s[n]=e[n]);return s}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(s[n]=e[n])}return s}var p=r.createContext({}),i=function(e){var t=r.useContext(p),n=t;return e&&(n="function"==typeof e?e(t):l(l({},t),e)),n},c=function(e){var t=i(e.components);return r.createElement(p.Provider,{value:t},e.children)},m="mdxType",u={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},d=r.forwardRef((function(e,t){var n=e.components,s=e.mdxType,a=e.originalType,p=e.parentName,c=o(e,["components","mdxType","originalType","parentName"]),m=i(n),d=s,y=m["".concat(p,".").concat(d)]||m[d]||u[d]||a;return n?r.createElement(y,l(l({ref:t},c),{},{components:n})):r.createElement(y,l({ref:t},c))}));function y(e,t){var n=arguments,s=t&&t.mdxType;if("string"==typeof e||s){var a=n.length,l=new Array(a);l[0]=d;var o={};for(var p in t)hasOwnProperty.call(t,p)&&(o[p]=t[p]);o.originalType=e,o[m]="string"==typeof e?e:s,l[1]=o;for(var i=2;i<a;i++)l[i]=n[i];return r.createElement.apply(null,l)}return r.createElement.apply(null,n)}d.displayName="MDXCreateElement"},5152:(e,t,n)=>{n.r(t),n.d(t,{Highlight:()=>c,assets:()=>p,contentTitle:()=>l,default:()=>d,frontMatter:()=>a,metadata:()=>o,toc:()=>i});var r=n(7462),s=(n(7294),n(3905));const a={title:"\u7b80\u4ecb",hide_title:!0,hide_table_of_contents:!1,slug:"/"},l=void 0,o={unversionedId:"\u7b80\u4ecb",id:"\u7b80\u4ecb",title:"\u7b80\u4ecb",description:"PyPI",source:"@site/docs/0.\u7b80\u4ecb.mdx",sourceDirName:".",slug:"/",permalink:"/pywss/",draft:!1,editUrl:"https://github.com/czasg/pywss/edit/docs/docs/0.\u7b80\u4ecb.mdx",tags:[],version:"current",sidebarPosition:0,frontMatter:{title:"\u7b80\u4ecb",hide_title:!0,hide_table_of_contents:!1,slug:"/"},sidebar:"tutorialSidebar",next:{title:"\u5feb\u901f\u4e0a\u624b",permalink:"/pywss/start"}},p={},i=[{value:"Pywss",id:"pywss",level:2},{value:"Example",id:"example",level:2},{value:"Why",id:"why",level:2}],c=e=>{let{children:t}=e;return(0,s.kt)("span",{style:{backgroundColor:"#f1f0d8",borderRadius:"10px",color:"#000",padding:"0.4rem",fontWeight:700}},t)},m={toc:i,Highlight:c},u="wrapper";function d(e){let{components:t,...n}=e;return(0,s.kt)(u,(0,r.Z)({},m,n,{components:t,mdxType:"MDXLayout"}),(0,s.kt)("admonition",{title:"\u5f53\u524d\u6700\u65b0\u7248\u672c",type:"note"},(0,s.kt)("p",{parentName:"admonition"},(0,s.kt)("img",{parentName:"p",src:"https://img.shields.io/pypi/v/pywss?color=green",alt:"PyPI"}),"\n",(0,s.kt)("img",{parentName:"p",src:"https://img.shields.io/codecov/c/github/czasg/pywss?token=JSXIQXY1EQ",alt:"Codecov"}))),(0,s.kt)("h2",{id:"pywss"},"Pywss"),(0,s.kt)("p",null,"Pywss\uff08\u53d1\u97f3 /pi\u02d0wa\u026az/\uff0c\u7c7b\u4f3c ",(0,s.kt)("strong",{parentName:"p"},"p~whys"),"\uff09\u662f\u4e00\u4e2a\u8f7b\u91cf\u7ea7\u7684 Python Web \u6846\u67b6\uff0c\u5b83\u57fa\u4e8e Python3.6+ \u7279\u6027\u6784\u5efa\u3002"),(0,s.kt)("p",null,"\u4e0e Flask\u3001Django \u7b49\u4e3b\u6d41\u6846\u67b6\u4e0d\u540c\u7684\u662f\uff0cPywss \u7684\u5e95\u5c42\u5e76\u6ca1\u6709\u5b9e\u73b0 WSGI \u63a5\u53e3\u534f\u8bae\u3002\n\u5176\u7f16\u7a0b\u98ce\u683c\u4e5f\u66f4\u7c7b\u4f3c\u4e8e Gin\u3001Iris \u7b49\u6846\u67b6\uff0c\u56e0\u6b64\u5bf9\u4e8e\u719f\u6089\u8fd9\u4e9b\u6846\u67b6\u7684\u5f00\u53d1\u8005\u6765\u8bf4\uff0cPywss \u662f\u4e00\u4e2a\u975e\u5e38\u503c\u5f97\u63a2\u7d22\u7684\u9879\u76ee\u3002"),(0,s.kt)("p",null,"\u5176\u5173\u952e\u7279\u6027\u6709\uff1a"),(0,s.kt)("ul",null,(0,s.kt)("li",{parentName:"ul"},(0,s.kt)("strong",{parentName:"li"},"\u7b80\u5355"),"\uff1a\u62d2\u7edd\u6d77\u91cf\u53c2\u6570\uff0c\u51cf\u5c11\u5fc3\u667a\u8d1f\u62c5\u3002\u4e86\u89e3\u4e0a\u4e0b\u6587 ",(0,s.kt)(c,{mdxType:"Highlight"},"pywss.Context")," \u5373\u523b\u542f\u7a0b\u3002"),(0,s.kt)("li",{parentName:"ul"},(0,s.kt)("strong",{parentName:"li"},"\u5feb\u901f"),"\uff1a\u7eaf\u624b\u64b8 socket\uff0c\u62d2\u7edd\u4e2d\u95f4\u5546\u8d5a\u53d6\u6027\u80fd\u5dee\u4ef7\u3002(\u5b9e\u5728\u6709\u6027\u80fd\u8ffd\u6c42\u7684\u540c\u5b66\uff0c\u4e0d\u59a8\u518d\u63a2\u7d22\u4e0b\u5176\u4ed6\u8bed\u8a00~",(0,s.kt)("strong",{parentName:"li"},"Go"),"~)"),(0,s.kt)("li",{parentName:"ul"},(0,s.kt)("strong",{parentName:"li"},"\u4f18\u96c5"),"\uff1a",(0,s.kt)(c,{mdxType:"Highlight"},"next")," \u8bbe\u8ba1\u771f\u7684\u592a\u4f18\u96c5\u4e86\u3002\u5982\u679c\u4f60\u4e5f\u548c\u6211\u4e00\u6837\u559c\u6b22\uff0c\u90a3\u6211\u89c9\u5f97\u8fd9\u4ef6\u4e8b\u60c5\uff0c",(0,s.kt)("strong",{parentName:"li"},"\u6cf0\u88e4\u8fa3\uff01\uff01")),(0,s.kt)("li",{parentName:"ul"},(0,s.kt)("strong",{parentName:"li"},"\u6807\u51c6"),"\uff1a\u96c6\u6210\u4e86\u90e8\u5206 OpenAPI\uff08Swagger\uff09\u80fd\u529b\uff0c\u65b9\u4fbf\u5f00\u53d1\u8005\u5feb\u901f\u751f\u6210 API \u6587\u6863\u5e76\u8fdb\u884c\u8c03\u8bd5\u3002"),(0,s.kt)("li",{parentName:"ul"},(0,s.kt)("strong",{parentName:"li"},"\u6d4b\u8bd5"),"\uff1a\u5f00\u7bb1\u5373\u7528\u7684 ",(0,s.kt)("strong",{parentName:"li"},"API \u6d4b\u8bd5\u6a21\u5757"),"\uff0c\u4e0d\u542f\u52a8\u670d\u52a1\u4e5f\u80fd\u6d4b\u8bd5\u63a5\u53e3\u529f\u80fd\u8fa3\uff01"),(0,s.kt)("li",{parentName:"ul"},(0,s.kt)("strong",{parentName:"li"},"\u5de5\u5177\u94fe"),"\uff1a\u5f00\u7bb1\u5373\u7528\u7684\u5de5\u5177\u5e93\uff0c\u63d0\u4f9b ",(0,s.kt)("strong",{parentName:"li"},"WebSocket")," \u7b49\u80fd\u529b\u3002")),(0,s.kt)("h2",{id:"example"},"Example"),(0,s.kt)("p",null,"\u4ee5\u4e0b\u5c55\u793a\u4e86\u4e00\u4e9b\u6700\u57fa\u672c\u7684\u7528\u4f8b\uff0c\u5982\u679c\u4f60\u6709\u4e00\u5b9a\u540e\u7aef\u7f16\u7a0b\u57fa\u7840\uff0c\u76f8\u4fe1\u4f60\u770b\u5b8c\u8fd9\u4e9b\u7528\u4f8b\uff0c\u5927\u6982\u5c31\u77e5\u9053 Pywss \u505a\u4e86\u4ec0\u4e48\u4e8b\u60c5\u4e86\u3002"),(0,s.kt)("pre",null,(0,s.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="\u4e00\u4e2a\u7b80\u5355\u7684\u5e94\u7528" showLineNumbers',title:'"\u4e00\u4e2a\u7b80\u5355\u7684\u5e94\u7528"',showLineNumbers:!0},'import pywss\n\napp = pywss.App()\napp.get("/hello", lambda ctx: ctx.write("HelloWorld"))\napp.run()\n')),(0,s.kt)("pre",null,(0,s.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="\u4f18\u96c5\u5b9e\u73b0 log \u4e2d\u95f4\u4ef6" showLineNumbers {6}',title:'"\u4f18\u96c5\u5b9e\u73b0',log:!0,'\u4e2d\u95f4\u4ef6"':!0,showLineNumbers:!0,"{6}":!0},'import pywss\nimport time\n\ndef logMiddleware(ctx: pywss.Context):\n    startTime = time.time()\n    ctx.next()  # \u6267\u884c\u4e0b\u4e00\u4e2ahandler\n    cost = time.time() - startTime\n    print(f"{ctx.method} - {ctx.route} - cost: {cost: .2f}")\n')),(0,s.kt)("pre",null,(0,s.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="\u4f18\u96c5\u5b9e\u73b0 cors \u4e2d\u95f4\u4ef6" showLineNumbers {11}',title:'"\u4f18\u96c5\u5b9e\u73b0',cors:!0,'\u4e2d\u95f4\u4ef6"':!0,showLineNumbers:!0,"{11}":!0},'import pywss\nimport time\n\ndef corsMiddleware(ctx: pywss.Context):\n    ctx.set_header(pywss.HeaderAccessControlAllowOrigin, "*")\n    ctx.set_header(pywss.HeaderAccessControlAllowMethods, "*")\n    ctx.set_header(pywss.HeaderAccessControlAllowHeaders, "*")\n    ctx.set_header(pywss.HeaderAccessControlAllowCredentials, "true")\n    if ctx.method == pywss.MethodOptions:\n        return\n    ctx.next()  # \u6267\u884c\u4e0b\u4e00\u4e2ahandler\uff0c\u82e5\u4e0d\u8c03\u7528\uff0c\u5219\u5f53\u524dhandler\u4e3a\u6700\u540e\u6267\u884c\u903b\u8f91\n')),(0,s.kt)("pre",null,(0,s.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="swagger" showLineNumbers {3,8}',title:'"swagger"',showLineNumbers:!0,"{3,8}":!0},'import pywss\n\n@pywss.openapi.docs("\u63a5\u53e3\u8bf4\u660e")\ndef hello(ctx: pywss.Context):\n    pass\n\napp = pywss.App()\napp.openapi()  # \u542f\u52a8openapi\napp.get("/hello", hello)\napp.run()\n')),(0,s.kt)("pre",null,(0,s.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="websocket" showLineNumbers {4}',title:'"websocket"',showLineNumbers:!0,"{4}":!0},'import pywss\n\ndef helloWS(ctx: pywss.Context):\n    err = pywss.WebSocketUpgrade(ctx)\n    if err:\n        return\n    ctx.ws_read()\n    crx.ws_write()\n\napp = pywss.App()\napp.get("/hello/ws", helloWS)\napp.run()\n')),(0,s.kt)("pre",null,(0,s.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="\u63a5\u53e3\u6d4b\u8bd5" showLineNumbers {6}',title:'"\u63a5\u53e3\u6d4b\u8bd5"',showLineNumbers:!0,"{6}":!0},'import pywss\n\napp = pywss.App()\napp.get("/hello", lambda ctx: ctx.write("HelloWorld"))\n\nreq = pywss.HttpTestRequest(app)  # \u57fa\u4e8eapp\u521b\u5efaHttpRequest\nresp = req.get("/hello")  # \u53d1\u8d77Get\u8bf7\u6c42\uff0c\u83b7\u53d6resp\nassert resp.status_code == 200\nassert resp.body == "HelloWorld"\n')),(0,s.kt)("h2",{id:"why"},"Why"),(0,s.kt)("p",null,"\u53ef\u80fd\u5927\u90e8\u5206\u4f1a\u540c\u5b66\u5bf9 Python Web \u6846\u67b6\u611f\u89c9\u5230\u538c\u70e6..."),(0,s.kt)("p",null,"\u56e0\u4e3a\u5b83\u4eec\u7684\u9009\u62e9\u5b9e\u5728\u662f\u592a\u591a\u4e86\uff0c\u4f60\u751a\u81f3\u53ef\u4ee5\u8f7b\u6613\u7684\u8bf4\u51fa\u4e94\u79cd\u4ee5\u4e0a\u7684\u6846\u67b6\uff0c\u5305\u62ec\uff1aFlask\u3001Django\u3001Tornado\u3001FastAPI\u3001Bottle\u7b49\u7b49\u3002\n\u6bcf\u4e2a\u6846\u67b6\u90fd\u6709\u81ea\u5df1\u7684\u7279\u70b9\u548c\u9002\u7528\u573a\u666f\u3002\u5728\u9009\u62e9\u9002\u5408\u4f60\u9879\u76ee\u9700\u6c42\u7684\u6846\u67b6\u65f6\uff0c\u8fd9\u4e9b\u4e30\u5bcc\u7684\u9009\u62e9\u5f80\u5f80\u4f1a\u6210\u4e3a\u7ea0\u7ed3\u70b9\u3002"),(0,s.kt)("p",null,"\u5728\u8fd9\u79cd\u80cc\u666f\u4e0b\uff0cPywss \u8bde\u751f\u4e86\uff0c\u5c3d\u7ba1\u6211\u77e5\u9053\u5728\u4f60\u7684\u9009\u62e9\u4e2d\uff0cPywss \u4f1a\u662f\u672b\u5c3e\u751a\u81f3\u6392\u4e0d\u4e0a\u4f4d\u3002"),(0,s.kt)(c,{mdxType:"Highlight"},"\u4f46 Pywss \u81f4\u529b\u4e8e\u8ffd\u6c42\u771f\u6b63\u7684\u8f7b\u91cf\u7ea7\u3002"),(0,s.kt)("br",null),(0,s.kt)("br",null),(0,s.kt)("p",null,"\u6216\u8bb8\u4f60\u4f1a\u89c9\u5f97 Flask \u8db3\u591f\u8f7b\u91cf\uff0c\u4f46\u5982\u679c\u4f60\u4e0d\u4e86\u89e3 ",(0,s.kt)("strong",{parentName:"p"},"ThreadLocalData\u3001RequestHook\u3001Blueprints\u3001g")," \u7b49\u76f8\u5173\u6982\u5ff5\u53ca\u539f\u7406\uff0c\u6211\u751a\u81f3\u4f1a\u89c9\u5f97\u4f60\u6ca1\u6709\u5165\u95e8\u3002"),(0,s.kt)("p",null,"\u8bf4\u5230\u5e95\uff0c\u5f53\u4ee3 Web \u6846\u67b6\u529f\u80fd\u592a\u591a\u4e86\uff0c\u591a\u5230\u4f60\u8bb0\u4e0d\u5b8c\u7684\u53c2\u6570\u3001\u5199\u4e0d\u660e\u767d\u7684\u914d\u7f6e\u3001\u7ffb\u4e0d\u5b8c\u7684\u6587\u6863..."),(0,s.kt)("p",null,"\u6240\u4ee5\uff0c\u5982\u679c\u4f60\u521a\u597d\u6709\u4e00\u4e2a\u975e\u6b63\u5f0f\u7684\u9879\u76ee\uff0c\u4e5f\u521a\u597d\u5728\u9009\u62e9\u5408\u9002\u7684\u6846\u67b6..."),(0,s.kt)("p",null,"\u6211\u4f1a\u63a8\u8350\u4f60\u4f7f\u7528 Pywss \uff01\uff01"))}d.isMDXComponent=!0}}]);