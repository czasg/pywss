"use strict";(self.webpackChunkpywss_docs=self.webpackChunkpywss_docs||[]).push([[176],{3905:(t,e,n)=>{n.d(e,{Zo:()=>d,kt:()=>N});var a=n(7294);function r(t,e,n){return e in t?Object.defineProperty(t,e,{value:n,enumerable:!0,configurable:!0,writable:!0}):t[e]=n,t}function l(t,e){var n=Object.keys(t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(t);e&&(a=a.filter((function(e){return Object.getOwnPropertyDescriptor(t,e).enumerable}))),n.push.apply(n,a)}return n}function i(t){for(var e=1;e<arguments.length;e++){var n=null!=arguments[e]?arguments[e]:{};e%2?l(Object(n),!0).forEach((function(e){r(t,e,n[e])})):Object.getOwnPropertyDescriptors?Object.defineProperties(t,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(e){Object.defineProperty(t,e,Object.getOwnPropertyDescriptor(n,e))}))}return t}function p(t,e){if(null==t)return{};var n,a,r=function(t,e){if(null==t)return{};var n,a,r={},l=Object.keys(t);for(a=0;a<l.length;a++)n=l[a],e.indexOf(n)>=0||(r[n]=t[n]);return r}(t,e);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(t);for(a=0;a<l.length;a++)n=l[a],e.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(t,n)&&(r[n]=t[n])}return r}var o=a.createContext({}),s=function(t){var e=a.useContext(o),n=e;return t&&(n="function"==typeof t?t(e):i(i({},e),t)),n},d=function(t){var e=s(t.components);return a.createElement(o.Provider,{value:e},t.children)},m="mdxType",u={inlineCode:"code",wrapper:function(t){var e=t.children;return a.createElement(a.Fragment,{},e)}},k=a.forwardRef((function(t,e){var n=t.components,r=t.mdxType,l=t.originalType,o=t.parentName,d=p(t,["components","mdxType","originalType","parentName"]),m=s(n),k=r,N=m["".concat(o,".").concat(k)]||m[k]||u[k]||l;return n?a.createElement(N,i(i({ref:e},d),{},{components:n})):a.createElement(N,i({ref:e},d))}));function N(t,e){var n=arguments,r=e&&e.mdxType;if("string"==typeof t||r){var l=n.length,i=new Array(l);i[0]=k;var p={};for(var o in e)hasOwnProperty.call(e,o)&&(p[o]=e[o]);p.originalType=t,p[m]="string"==typeof t?t:r,i[1]=p;for(var s=2;s<l;s++)i[s]=n[s];return a.createElement.apply(null,i)}return a.createElement.apply(null,n)}k.displayName="MDXCreateElement"},5162:(t,e,n)=>{n.d(e,{Z:()=>i});var a=n(7294),r=n(6010);const l={tabItem:"tabItem_Ymn6"};function i(t){let{children:e,hidden:n,className:i}=t;return a.createElement("div",{role:"tabpanel",className:(0,r.Z)(l.tabItem,i),hidden:n},e)}},4866:(t,e,n)=>{n.d(e,{Z:()=>x});var a=n(7462),r=n(7294),l=n(6010),i=n(2466),p=n(6550),o=n(1980),s=n(7392),d=n(12);function m(t){return function(t){return r.Children.map(t,(t=>{if(!t||(0,r.isValidElement)(t)&&function(t){const{props:e}=t;return!!e&&"object"==typeof e&&"value"in e}(t))return t;throw new Error(`Docusaurus error: Bad <Tabs> child <${"string"==typeof t.type?t.type:t.type.name}>: all children of the <Tabs> component should be <TabItem>, and every <TabItem> should have a unique "value" prop.`)}))?.filter(Boolean)??[]}(t).map((t=>{let{props:{value:e,label:n,attributes:a,default:r}}=t;return{value:e,label:n,attributes:a,default:r}}))}function u(t){const{values:e,children:n}=t;return(0,r.useMemo)((()=>{const t=e??m(n);return function(t){const e=(0,s.l)(t,((t,e)=>t.value===e.value));if(e.length>0)throw new Error(`Docusaurus error: Duplicate values "${e.map((t=>t.value)).join(", ")}" found in <Tabs>. Every value needs to be unique.`)}(t),t}),[e,n])}function k(t){let{value:e,tabValues:n}=t;return n.some((t=>t.value===e))}function N(t){let{queryString:e=!1,groupId:n}=t;const a=(0,p.k6)(),l=function(t){let{queryString:e=!1,groupId:n}=t;if("string"==typeof e)return e;if(!1===e)return null;if(!0===e&&!n)throw new Error('Docusaurus error: The <Tabs> component groupId prop is required if queryString=true, because this value is used as the search param name. You can also provide an explicit value such as queryString="my-search-param".');return n??null}({queryString:e,groupId:n});return[(0,o._X)(l),(0,r.useCallback)((t=>{if(!l)return;const e=new URLSearchParams(a.location.search);e.set(l,t),a.replace({...a.location,search:e.toString()})}),[l,a])]}function c(t){const{defaultValue:e,queryString:n=!1,groupId:a}=t,l=u(t),[i,p]=(0,r.useState)((()=>function(t){let{defaultValue:e,tabValues:n}=t;if(0===n.length)throw new Error("Docusaurus error: the <Tabs> component requires at least one <TabItem> children component");if(e){if(!k({value:e,tabValues:n}))throw new Error(`Docusaurus error: The <Tabs> has a defaultValue "${e}" but none of its children has the corresponding value. Available values are: ${n.map((t=>t.value)).join(", ")}. If you intend to show no default tab, use defaultValue={null} instead.`);return e}const a=n.find((t=>t.default))??n[0];if(!a)throw new Error("Unexpected error: 0 tabValues");return a.value}({defaultValue:e,tabValues:l}))),[o,s]=N({queryString:n,groupId:a}),[m,c]=function(t){let{groupId:e}=t;const n=function(t){return t?`docusaurus.tab.${t}`:null}(e),[a,l]=(0,d.Nk)(n);return[a,(0,r.useCallback)((t=>{n&&l.set(t)}),[n,l])]}({groupId:a}),g=(()=>{const t=o??m;return k({value:t,tabValues:l})?t:null})();(0,r.useLayoutEffect)((()=>{g&&p(g)}),[g]);return{selectedValue:i,selectValue:(0,r.useCallback)((t=>{if(!k({value:t,tabValues:l}))throw new Error(`Can't select invalid tab value=${t}`);p(t),s(t),c(t)}),[s,c,l]),tabValues:l}}var g=n(2389);const h={tabList:"tabList__CuJ",tabItem:"tabItem_LNqP"};function b(t){let{className:e,block:n,selectedValue:p,selectValue:o,tabValues:s}=t;const d=[],{blockElementScrollPositionUntilNextRender:m}=(0,i.o5)(),u=t=>{const e=t.currentTarget,n=d.indexOf(e),a=s[n].value;a!==p&&(m(e),o(a))},k=t=>{let e=null;switch(t.key){case"Enter":u(t);break;case"ArrowRight":{const n=d.indexOf(t.currentTarget)+1;e=d[n]??d[0];break}case"ArrowLeft":{const n=d.indexOf(t.currentTarget)-1;e=d[n]??d[d.length-1];break}}e?.focus()};return r.createElement("ul",{role:"tablist","aria-orientation":"horizontal",className:(0,l.Z)("tabs",{"tabs--block":n},e)},s.map((t=>{let{value:e,label:n,attributes:i}=t;return r.createElement("li",(0,a.Z)({role:"tab",tabIndex:p===e?0:-1,"aria-selected":p===e,key:e,ref:t=>d.push(t),onKeyDown:k,onClick:u},i,{className:(0,l.Z)("tabs__item",h.tabItem,i?.className,{"tabs__item--active":p===e})}),n??e)})))}function f(t){let{lazy:e,children:n,selectedValue:a}=t;const l=(Array.isArray(n)?n:[n]).filter(Boolean);if(e){const t=l.find((t=>t.props.value===a));return t?(0,r.cloneElement)(t,{className:"margin-top--md"}):null}return r.createElement("div",{className:"margin-top--md"},l.map(((t,e)=>(0,r.cloneElement)(t,{key:e,hidden:t.props.value!==a}))))}function y(t){const e=c(t);return r.createElement("div",{className:(0,l.Z)("tabs-container",h.tabList)},r.createElement(b,(0,a.Z)({},t,e)),r.createElement(f,(0,a.Z)({},t,e)))}function x(t){const e=(0,g.Z)();return r.createElement(y,(0,a.Z)({key:String(e)},t))}},8028:(t,e,n)=>{n.r(e),n.d(e,{Highlight:()=>u,assets:()=>d,contentTitle:()=>o,default:()=>c,frontMatter:()=>p,metadata:()=>s,toc:()=>m});var a=n(7462),r=(n(7294),n(3905)),l=n(4866),i=n(5162);const p={title:"\u5feb\u901f\u4e0a\u624b",hide_title:!0,hide_table_of_contents:!1,slug:"/start"},o=void 0,s={unversionedId:"\u5feb\u901f\u4e0a\u624b",id:"\u5feb\u901f\u4e0a\u624b",title:"\u5feb\u901f\u4e0a\u624b",description:"\u5b89\u88c5",source:"@site/docs/1.\u5feb\u901f\u4e0a\u624b.mdx",sourceDirName:".",slug:"/start",permalink:"/pywss/start",draft:!1,editUrl:"https://github.com/czasg/pywss/edit/docs/docs/1.\u5feb\u901f\u4e0a\u624b.mdx",tags:[],version:"current",sidebarPosition:1,frontMatter:{title:"\u5feb\u901f\u4e0a\u624b",hide_title:!0,hide_table_of_contents:!1,slug:"/start"},sidebar:"tutorialSidebar",previous:{title:"\u7b80\u4ecb",permalink:"/pywss/"},next:{title:"\u8fdb\u9636\u4f7f\u7528",permalink:"/pywss/advance"}},d={},m=[{value:"\u5b89\u88c5",id:"\u5b89\u88c5",level:2},{value:"\u521b\u5efa\u5e94\u7528",id:"\u521b\u5efa\u5e94\u7528",level:2},{value:"1.\u9996\u5148\u662f\u521d\u59cb\u5316\u6a21\u5757",id:"1\u9996\u5148\u662f\u521d\u59cb\u5316\u6a21\u5757",level:4},{value:"2.\u5176\u6b21\u662f\u8def\u7531\u6ce8\u518c\u6a21\u5757",id:"2\u5176\u6b21\u662f\u8def\u7531\u6ce8\u518c\u6a21\u5757",level:4},{value:"\u4e0a\u4e0b\u6587 <strong>Context</strong>",id:"\u4e0a\u4e0b\u6587-context",level:2},{value:"\u4f18\u96c5\u7684\u4f7f\u7528 <strong>Next</strong>",id:"\u4f18\u96c5\u7684\u4f7f\u7528-next",level:2},{value:"\u539f\u7406\u7b80\u4ecb",id:"\u539f\u7406\u7b80\u4ecb",level:3},{value:"\u4f7f\u7528\u65b9\u6cd5",id:"\u4f7f\u7528\u65b9\u6cd5",level:3}],u=t=>{let{children:e}=t;return(0,r.kt)("span",{style:{backgroundColor:"#f1f0d8",borderRadius:"10px",color:"#000",padding:"0.4rem",fontWeight:700}},e)},k={toc:m,Highlight:u},N="wrapper";function c(t){let{components:e,...n}=t;return(0,r.kt)(N,(0,a.Z)({},k,n,{components:e,mdxType:"MDXLayout"}),(0,r.kt)("h2",{id:"\u5b89\u88c5"},"\u5b89\u88c5"),(0,r.kt)("p",null,"Pywss \u4f9d\u8d56 python 3.6+ \u7248\u672c\u7684\u90e8\u5206\u7279\u6027\u3002"),(0,r.kt)("p",null,"\u5982\u679c\u4f60\u521a\u597d\u4f7f\u7528\u7684\u662f 3.6 \u53ca\u4ee5\u4e0a\u7248\u672c\u7684\u8bdd\uff0c\u90a3\u4e48\u606d\u559c\u4f60\uff0c\u4f60\u53ef\u4ee5\u901a\u8fc7",(0,r.kt)("inlineCode",{parentName:"p"},"pip"),"\u5b9e\u73b0\u5feb\u901f\u5b89\u88c5\u3002"),(0,r.kt)(l.Z,{className:"unique-tabs",mdxType:"Tabs"},(0,r.kt)(i.Z,{value:"pip\u5b89\u88c5",label:"pip\u5b89\u88c5",default:!0,mdxType:"TabItem"},(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-shell"},">>> pip3 install pywss\n>>> pip3 install pywss -i https://pypi.org/simple\n>>> pip3 install pywss -i https://pypi.tuna.tsinghua.edu.cn/simple\n"))),(0,r.kt)(i.Z,{value:"\u6e90\u7801\u5b89\u88c5",label:"\u6e90\u7801\u5b89\u88c5",default:!0,mdxType:"TabItem"},(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-shell"},">>> git clone https://github.com/czasg/pywss.git\n>>> cd pywss\n>>> python3 setup.py install\n")))),(0,r.kt)("p",null,"Pywss \u76ee\u524d\u4ec5\u4f9d\u8d56\u4e00\u4e2a\u65e5\u5fd7\u5e93 ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/czasg/loggus"},"loggus"),"\uff0c\u8be5\u5e93\u662f\u4f5c\u8005\u5bf9\u7ed3\u6784\u5316\u65e5\u5fd7\u5e93\u7684\u63a2\u7d22\u6210\u679c\uff0c\u6682\u65f6\u591f\u7528\ud83d\ude05\u3002"),(0,r.kt)("p",null,"\u540e\u7eed\u4f1a\u8003\u8651\u5207\u56de\u539f\u751f\u65e5\u5fd7\u5e93 logging\uff0c\u51cf\u5c11\u5fc3\u667a\u8d1f\u62c5\ud83d\ude05\u3002"),(0,r.kt)("h2",{id:"\u521b\u5efa\u5e94\u7528"},"\u521b\u5efa\u5e94\u7528"),(0,r.kt)("p",null,"\u672c\u8282\u7ee7\u7eed\u4ee5 hello world \u4e3a\u4f8b\uff0c\u4ece\u96f6\u5f00\u59cb\u5feb\u901f\u642d\u5efa\u4e00\u4e2a web \u5e94\u7528\u3002"),(0,r.kt)("p",null,"\u9996\u5148\uff0c\u5728\u672c\u5730\u521b\u5efa ",(0,r.kt)("strong",{parentName:"p"},"main.py")," \u6587\u4ef6\u5e76\u5199\u5165\u4ee5\u4e0b\u6e90\u7801\u3002"),(0,r.kt)(l.Z,{className:"unique-tabs",mdxType:"Tabs"},(0,r.kt)(i.Z,{value:"main.py",label:"main.py",default:!0,mdxType:"TabItem"},(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python",metastring:'showLineNumbers title="\u6e90\u7801"',showLineNumbers:!0,title:'"\u6e90\u7801"'},'import pywss\n\ndef helloHandler(ctx: pywss.Context):\n    ctx.write({"hello": "world"})\n\ndef main(defaultPort = 8080):\n    app = pywss.App()\n    app.get("/hi", lambda ctx: ctx.write("hi~"))  # \u533f\u540d\u51fd\u6570\u4e5f\u662f\u4e0d\u9519\u7684\u9009\u62e9\n    app.post("/hello", helloHandler)\n    app.run(port=defaultPort)\n\nif __name__ == \'__main__\':\n    """\n    python3 main.py \u542f\u52a8\u670d\u52a1\n    """\n    main()\n'))),(0,r.kt)(i.Z,{value:"GET/hi",label:"GET/hi",mdxType:"TabItem"},(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-shell",metastring:'title="\u8bf7\u6c42 /hi \u63a5\u53e3"',title:'"\u8bf7\u6c42',"/hi":!0,'\u63a5\u53e3"':!0},">>> curl localhost:8080/hi\nhi~\n"))),(0,r.kt)(i.Z,{value:"POST/hello",label:"POST/hello",mdxType:"TabItem"},(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-shell",metastring:'title="\u8bf7\u6c42 /hello \u63a5\u53e3"',title:'"\u8bf7\u6c42',"/hello":!0,'\u63a5\u53e3"':!0},'>>> curl -X POST localhost:8080/hello\n{"hello": "world"}\n')))),(0,r.kt)("p",null,"\u5728 ",(0,r.kt)("strong",{parentName:"p"},(0,r.kt)("inlineCode",{parentName:"strong"},"main.py"))," \u4e2d\u6211\u4eec\u53ef\u4ee5\u770b\u5230\uff1a"),(0,r.kt)("h4",{id:"1\u9996\u5148\u662f\u521d\u59cb\u5316\u6a21\u5757"},"1.\u9996\u5148\u662f\u521d\u59cb\u5316\u6a21\u5757"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"\u5728\u7b2c7\u884c\u521d\u59cb\u5316\u4e86\u4e00\u4e2a",(0,r.kt)("inlineCode",{parentName:"li"},"app"),"\u3002"),(0,r.kt)("li",{parentName:"ul"},"\u5728\u7b2c10\u884c\u6267\u884c",(0,r.kt)("inlineCode",{parentName:"li"},"app.run"),"\u542f\u52a8 web \u5e94\u7528\u3002")),(0,r.kt)("p",null,"\u8fd9\u4e24\u884c\u4ee3\u7801\uff0c\u56ca\u62ec\u4e86 app \u4ece ",(0,r.kt)("strong",{parentName:"p"},"\u521d\u59cb\u5316 -> \u542f\u52a8")," \u7684\u6574\u4e2a\u5468\u671f\u3002"),(0,r.kt)("h4",{id:"2\u5176\u6b21\u662f\u8def\u7531\u6ce8\u518c\u6a21\u5757"},"2.\u5176\u6b21\u662f\u8def\u7531\u6ce8\u518c\u6a21\u5757"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},"\u7b2c8\u884c ",(0,r.kt)("strong",{parentName:"li"},(0,r.kt)("inlineCode",{parentName:"strong"},"app.get()"))," \u8868\u793a ",(0,r.kt)("strong",{parentName:"li"},"\u6ce8\u518c Http Get")," \u65b9\u6cd5\uff0c\u5176\u53c2\u6570\u5206\u522b\u8868\u793a\uff1a",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("strong",{parentName:"li"},"\u7ed1\u5b9a\u8def\u7531")," ",(0,r.kt)("inlineCode",{parentName:"li"},"/hi")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("strong",{parentName:"li"},"\u7ed1\u5b9a\u4e1a\u52a1\u5904\u7406\u903b\u8f91")," ",(0,r.kt)("inlineCode",{parentName:"li"},'lambda ctx: ctx.write("hi~")')))),(0,r.kt)("li",{parentName:"ul"},"\u7b2c9\u884c ",(0,r.kt)("strong",{parentName:"li"},(0,r.kt)("inlineCode",{parentName:"strong"},"app.post()"))," \u8868\u793a ",(0,r.kt)("strong",{parentName:"li"},"\u6ce8\u518c Http Post")," \u65b9\u6cd5\uff0c\u5176\u53c2\u6570\u5206\u522b\u8868\u793a\uff1a",(0,r.kt)("ul",{parentName:"li"},(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("strong",{parentName:"li"},"\u7ed1\u5b9a\u8def\u7531")," ",(0,r.kt)("inlineCode",{parentName:"li"},"/hello")),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("strong",{parentName:"li"},"\u7ed1\u5b9a\u4e1a\u52a1\u5904\u7406\u903b\u8f91")," ",(0,r.kt)("inlineCode",{parentName:"li"},"helloHandler"))))),(0,r.kt)("p",null,"\u901a\u8fc7 ",(0,r.kt)("inlineCode",{parentName:"p"},"python3 main.py")," \u542f\u52a8\u670d\u52a1\u540e\uff0c\u6211\u4eec\u53ef\u4ee5\u901a\u8fc7 ",(0,r.kt)("inlineCode",{parentName:"p"},"curl")," \u6765\u9a8c\u8bc1\u670d\u52a1\u3002\u7ed3\u679c\u89c1\u4e0a\u3002"),(0,r.kt)("p",null,"\u81f3\u6b64\uff0c\u4e00\u4e2a\u7b80\u5355\u7684 hello world \u5e94\u7528\u5c31\u642d\u5efa\u5b8c\u6210\u4e86\u3002"),(0,r.kt)("h2",{id:"\u4e0a\u4e0b\u6587-context"},"\u4e0a\u4e0b\u6587 ",(0,r.kt)("strong",{parentName:"h2"},"Context")),(0,r.kt)("p",null,"\u5728 Pywss \u4e2d\uff0c",(0,r.kt)("strong",{parentName:"p"},(0,r.kt)("inlineCode",{parentName:"strong"},"pywss.Context")),"\uff08\u540e\u6587\u5747\u4f7f\u7528 ctx \u4ee3\u66ff\uff09 ",(0,r.kt)("strong",{parentName:"p"},"\u8d2f\u7a7f\u4e8e\u5355\u6b21\u8bf7\u6c42\u7684\u6574\u4e2a\u751f\u547d\u5468\u671f"),"\uff0c\u662f Pywss \u7528\u4e8e\u7ba1\u7406\u8bf7\u6c42\u7684\u4e0a\u4e0b\u6587\u5bf9\u8c61\u3002"),(0,r.kt)("p",null,"\u5bf9\u4e8e Pywss \u7684 ",(0,r.kt)("strong",{parentName:"p"},"Handler"),"\uff08\u4e1a\u52a1\u903b\u8f91\u5904\u7406\u6a21\u5757\uff09 \u6765\u8bf4\uff0c\u4ec5\u4e14\u652f\u6301 ",(0,r.kt)("strong",{parentName:"p"},"ctx")," \u8fd9\u4e00\u4e2a\u53c2\u6570\u3002"),(0,r.kt)("p",null,"\u6240\u4ee5\uff0c",(0,r.kt)("strong",{parentName:"p"},"ctx")," \u662f\u4e00\u4e2a\u96c6 ",(0,r.kt)("strong",{parentName:"p"},"HTTP \u8bf7\u6c42\u62a5\u6587\u89e3\u6790\u3001HTTP \u54cd\u5e94\u62a5\u6587\u6784\u5efa\u3001\u4fe1\u606f\u4f20\u9012")," \u4e8e\u4e00\u4f53\u7684\u4e0a\u4e0b\u6587\u5bf9\u8c61\u3002"),(0,r.kt)("p",null,"\u5176\u4e3b\u8981\u5c5e\u6027\u6709\uff1a"),(0,r.kt)("table",null,(0,r.kt)("thead",{parentName:"table"},(0,r.kt)("tr",{parentName:"thead"},(0,r.kt)("th",{parentName:"tr",align:null},"\u5c5e\u6027"),(0,r.kt)("th",{parentName:"tr",align:null},"\u7c7b\u578b"),(0,r.kt)("th",{parentName:"tr",align:null},"\u8bf4\u660e"))),(0,r.kt)("tbody",{parentName:"table"},(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.app"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"pywss.App")),(0,r.kt)("td",{parentName:"tr",align:null},"\u6839 ",(0,r.kt)("strong",{parentName:"td"},"app")," \u5bf9\u8c61")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.fd"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"socket.socket")),(0,r.kt)("td",{parentName:"tr",align:null},"sock\u53e5\u67c4\uff0c\u7528\u4e8e",(0,r.kt)("strong",{parentName:"td"},"\u5199\u64cd\u4f5c"),"\uff0c\u4e00\u822c\u4e0d\u76f4\u63a5\u4f7f\u7528")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.rfd"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"socket.makefile")),(0,r.kt)("td",{parentName:"tr",align:null},"sock\u53e5\u67c4\uff0c\u7528\u4e8e",(0,r.kt)("strong",{parentName:"td"},"\u8bfb\u64cd\u4f5c"),"\uff0c\u4e00\u822c\u4e0d\u76f4\u63a5\u4f7f\u7528")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.address"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"tuple")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u5730\u5740\u4fe1\u606f"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.method"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"str")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42\u65b9\u6cd5"),"\uff0c\u7531 GET/POST/PUT/DELETE/HEAD/PATCH/OPTIONS \u7ec4\u6210")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.version"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"str")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u534f\u8bae\u7248\u672c\u53f7"),"\uff0c\u53c2\u8003\u503c\uff1a",(0,r.kt)("inlineCode",{parentName:"td"},"HTTP/1.1"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.url"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"str")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42URL\u5730\u5740"),"\uff0c\u6ce8\u610f\u662f",(0,r.kt)("strong",{parentName:"td"},"\u5305\u542b\u8bf7\u6c42\u53c2\u6570\u5728\u5185"),"\u7684\u5168\u91cf\u5730\u5740\u3002\u53c2\u8003\u503c\uff1a",(0,r.kt)("inlineCode",{parentName:"td"},"/api/v1/query?key=value"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.url_params"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"dict")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42\u53c2\u6570"),"\uff0c\u662f\u57fa\u4e8e",(0,r.kt)("inlineCode",{parentName:"td"},"ctx.url"),"\u89e3\u6790\u7684\u7ed3\u679c\u3002\u4e3e\u4f8b\u8bf4\u660e\uff1a\u5bf9\u4e8e",(0,r.kt)("inlineCode",{parentName:"td"},"/api/v1/query?key=value"),"\u5730\u5740\uff0c",(0,r.kt)("inlineCode",{parentName:"td"},"ctx.url_params"),"\u7b49\u4e8e",(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},'{"key": "value"}')))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.route"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"str")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42\u8def\u7531"),"\uff0c\u6ce8\u610f\u662f",(0,r.kt)("strong",{parentName:"td"},"\u4e0d\u5305\u542b\u8bf7\u6c42\u53c2\u6570\u5728\u5185"),"\u7684\u8def\u7531\uff0c\u53c2\u8003\uff1a",(0,r.kt)("inlineCode",{parentName:"td"},"/api/v1/query"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.route_params"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"dict")),(0,r.kt)("td",{parentName:"tr",align:null},"\u7528\u4e8e\u5b58\u50a8",(0,r.kt)("a",{parentName:"td",href:"advance/route-match"},"\u5c40\u90e8\u5339\u914d"),"\u4e0b\u7684\u8def\u5f84\u53c2\u6570\uff0c\u4e3e\u4f8b\u8bf4\u660e\uff1a\u5bf9\u4e8e",(0,r.kt)("inlineCode",{parentName:"td"},"/api/v1/{name}/{age}"),"\u8def\u7531\uff0c",(0,r.kt)("inlineCode",{parentName:"td"},"ctx.route_params"),"\u7b49\u4e8e",(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},'{"name": "xx", "age": "xx"}')))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.headers"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"dict")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42\u5934"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.cookies"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"dict")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42Cookie"),"\uff0c\u662f\u57fa\u4e8e",(0,r.kt)("inlineCode",{parentName:"td"},'ctx.headers["Cookie"]'),"\u89e3\u6790\u7684\u7ed3\u679c")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.content_length"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"int")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42\u5927\u5c0f"),"\uff0c\u662f\u57fa\u4e8e",(0,r.kt)("inlineCode",{parentName:"td"},'ctx.headers["Content-Length"]'),"\u89e3\u6790\u7684\u7ed3\u679c")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.content"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"byte")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"HTTP\u8bf7\u6c42\u6570\u636e\u4f53"),"\u3002\u4e00\u822c\u4e0d\u76f4\u63a5\u4f7f\u7528\uff0c\u5bf9\u4e8e\u9700\u8981\u83b7\u53d6\u539f\u751f\u8bf7\u6c42\u573a\u666f\uff0c",(0,r.kt)("strong",{parentName:"td"},"\u63a8\u8350\u4f7f\u7528",(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.body()")))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.data"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"pywss.Data")),(0,r.kt)("td",{parentName:"tr",align:null},"\u57fa\u4e8e\u5b57\u5178\u5b9e\u73b0\uff0c",(0,r.kt)("strong",{parentName:"td"},"\u7528\u4e8eContext\u4e0a\u4e0b\u6587\u4fe1\u606f\u4f20\u9012"),"\u3002\u4f7f\u7528\u65b9\u5f0f\u53c2\u8003 ",(0,r.kt)("inlineCode",{parentName:"td"},"ctx.data.key = value"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.body()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("a",{parentName:"td",href:"advance/request-parse#byte"},(0,r.kt)("strong",{parentName:"a"},"\u89e3\u6790\u8bf7\u6c42")),"\uff0c\u4ee5 ",(0,r.kt)("strong",{parentName:"td"},"BYTE")," \u5f62\u5f0f\u8fd4\u56de")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.json()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("a",{parentName:"td",href:"advance/request-parse#json"},(0,r.kt)("strong",{parentName:"a"},"\u89e3\u6790\u8bf7\u6c42")),"\uff0c\u4ee5 ",(0,r.kt)("strong",{parentName:"td"},"JSON")," \u5f62\u5f0f\u8fd4\u56de")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.form()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("a",{parentName:"td",href:"advance/request-parse#form"},(0,r.kt)("strong",{parentName:"a"},"\u89e3\u6790\u8bf7\u6c42")),"\uff0c\u4ee5 ",(0,r.kt)("strong",{parentName:"td"},"FORM")," \u5f62\u5f0f\u8fd4\u56de")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.file()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("a",{parentName:"td",href:"advance/request-parse#file"},(0,r.kt)("strong",{parentName:"a"},"\u89e3\u6790\u8bf7\u6c42")),"\uff0c\u4ee5 ",(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"Dict[str, pywss.File]"))," \u5f62\u5f0f\u8fd4\u56de")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.stream()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("a",{parentName:"td",href:"advance/request-parse#stream"},(0,r.kt)("strong",{parentName:"a"},"\u6d41\u5f0f\u8bfb\u53d6\u8bf7\u6c42")),"\uff0c\u7528\u4e8e\u67d0\u4e9b\u5927\u6570\u636e\u573a\u666f")),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.set_status_code()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},"\u6307\u5b9aHTTP\u54cd\u5e94\u62a5\u6587",(0,r.kt)("strong",{parentName:"td"},"\u72b6\u6001\u7801"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.set_header()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},"\u6307\u5b9aHTTP",(0,r.kt)("strong",{parentName:"td"},"\u54cd\u5e94\u5934"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.set_content_type()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},"\u6307\u5b9aHTTP",(0,r.kt)("strong",{parentName:"td"},"\u54cd\u5e94\u7c7b\u578b"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.set_cookie()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},"\u6307\u5b9aHTTP",(0,r.kt)("strong",{parentName:"td"},"\u54cd\u5e94Cookie"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.write()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},"\u6307\u5b9aHTTP",(0,r.kt)("strong",{parentName:"td"},"\u54cd\u5e94\u4f53"),"\uff0c\u652f\u6301 ",(0,r.kt)("strong",{parentName:"td"},"String\u3001JSON\u3001Chunked")," \u7b49\uff0c\u8be6\u60c5\u89c1",(0,r.kt)("a",{parentName:"td",href:"advance/response"},"\u54cd\u5e94\u6a21\u5757"))),(0,r.kt)("tr",{parentName:"tbody"},(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.flush()"))),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("inlineCode",{parentName:"td"},"func")),(0,r.kt)("td",{parentName:"tr",align:null},(0,r.kt)("strong",{parentName:"td"},"\u53d1\u9001HTTP\u54cd\u5e94\u62a5\u6587"),"\uff0c\u4e00\u822c\u4e0d\u9700\u8981\u81ea\u5df1\u8c03\u7528\u3002",(0,r.kt)("inlineCode",{parentName:"td"},"flush"),"\u4ec5\u4e14\u53ea\u80fd\u8c03\u7528\u4e00\u6b21\uff0c\u591a\u6b21\u8c03\u7528\u4ec5\u7b2c\u4e00\u6b21\u751f\u6548~")))),(0,r.kt)("h2",{id:"\u4f18\u96c5\u7684\u4f7f\u7528-next"},"\u4f18\u96c5\u7684\u4f7f\u7528 ",(0,r.kt)("strong",{parentName:"h2"},"Next")),(0,r.kt)("admonition",{title:"\u524d\u63d0\u8bf4\u660e",type:"caution"},(0,r.kt)("p",{parentName:"admonition"},"\u672c\u8282\u6e90\u4ee3\u7801\u53d6\u81ea ",(0,r.kt)("strong",{parentName:"p"},"v0.1.18")," \u7248\u672c\uff0c\u6700\u65b0\u4ee3\u7801\u8bf7\u53c2\u8003 ",(0,r.kt)("a",{parentName:"p",href:"https://github.com/czasg/pywss"},"Github-Pywss"))),(0,r.kt)("h3",{id:"\u539f\u7406\u7b80\u4ecb"},"\u539f\u7406\u7b80\u4ecb"),(0,r.kt)("p",null,(0,r.kt)("strong",{parentName:"p"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.next"))," \u672c\u8d28\u662f\u4e00\u4e2a",(0,r.kt)("strong",{parentName:"p"},"\u5d4c\u5957\u8c03\u7528"),"\u3002"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python",metastring:'showLineNumbers title="\u793a\u4f8b"',showLineNumbers:!0,title:'"\u793a\u4f8b"'},'# \u5b9a\u4e49\u591a\u4e2ahandler\nhandler_1 = lambda ctx: ctx.next()  # \u89e6\u53d1handler_2\nhandler_2 = lambda ctx: ctx.next()  # \u89e6\u53d1handler_3\nhandler_3 = lambda ctx: ctx.next()  # \u65e0\u6548\n\n# \u6ce8\u518c\u591a\u4e2ahandler\napp.get("/hello", handler_1, handler_2, handler_3)\n\n# \u901a\u8fc7next\u5d4c\u5957\u8c03\u7528\u5b9e\u73b0\u540c\u7b49\u66ff\u6362\u7684\u6548\u679c\nctx.next() -> handler_1(ctx)  # \u7b2c\u4e00\u6b21\u8c03\u7528\u7b49\u540c\u4e8ehandler_1(ctx)\nctx.next() -> handler_2(ctx)  # \u7b2c\u4e8c\u6b21\u8c03\u7528\u7b49\u540c\u4e8ehandler_2(ctx)\nctx.next() -> handler_3(ctx)  # \u7b2c\u4e09\u6b21\u8c03\u7528\u7b49\u540c\u4e8ehandler_3(ctx)\nctx.next() -> None            # \u7b2c\u56db\u6b21\u8c03\u7528\uff0c\u65e0\u6548\n')),(0,r.kt)("p",null,"\u5176\u6e90\u7801\u4e5f\u662f\u975e\u5e38\u7684\u7b80\u6d01\uff0c\u6838\u5fc3\u903b\u8f91\u4ec5\u7531\u51e0\u884c\u4ee3\u7801\u5b9e\u73b0\uff1a"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python",metastring:'showLineNumbers title="ctx.next \u6e90\u7801"',showLineNumbers:!0,title:'"ctx.next','\u6e90\u7801"':!0},"def next(self) -> None:\n    if self._handler_index >= len(self._handlers):\n        return\n    index = self._handler_index\n    self._handler_index += 1\n    self._handlers[index](self)\n")),(0,r.kt)("p",null,"\u5177\u4f53\u5b9e\u73b0\u6d41\u7a0b\u6b64\u5904\u4e0d\u5c55\u5f00\uff0c\u611f\u5174\u8da3\u7684\u540c\u5b66\u53ef\u4ee5\u76f4\u63a5\u9605\u8bfb",(0,r.kt)("a",{parentName:"p",href:"https://github.com/czasg/pywss"},"\u6e90\u7801"),"\u3002"),(0,r.kt)("h3",{id:"\u4f7f\u7528\u65b9\u6cd5"},"\u4f7f\u7528\u65b9\u6cd5"),(0,r.kt)("p",null,"\u57fa\u4e8e ",(0,r.kt)("strong",{parentName:"p"},(0,r.kt)("inlineCode",{parentName:"strong"},"ctx.next"))," \u5d4c\u5957\u8c03\u7528\u7684\u7279\u6027\uff0c\u6211\u4eec\u53ef\u4ee5\u987a\u5e8f\u7684\u9009\u62e9 ",(0,r.kt)("strong",{parentName:"p"},"\u6267\u884c/\u4e0d\u6267\u884c")," \u540e\u9762\u7684handler\uff0c\u56e0\u6b64\u6211\u4eec\u53ef\u4ee5\u975e\u5e38\u5bb9\u6613\u7684\u5b9e\u73b0",(0,r.kt)("strong",{parentName:"p"},"\u4e2d\u95f4\u4ef6\u62d3\u5c55"),"\u3002"),(0,r.kt)("p",null,"\u5728 pywss \u4e2d\uff0c\u63d0\u4f9b\u4e86\u4e24\u79cd\u65b9\u5f0f\u6765\u62d3\u5c55\u4e2d\u95f4\u4ef6\u80fd\u529b\uff1a"),(0,r.kt)("ul",null,(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("strong",{parentName:"li"},"app use \u5168\u5c40\u6ce8\u518c")," \uff0c\u9488\u5bf9\u5168\u90e8\u8def\u7531\u751f\u6548"),(0,r.kt)("li",{parentName:"ul"},(0,r.kt)("strong",{parentName:"li"},"route bind \u5c40\u90e8\u6ce8\u518c")," \uff0c\u9488\u5bf9\u6307\u5b9a\u8def\u7531\u751f\u6548")),(0,r.kt)("p",null,"\u4e0b\u9762\u901a\u8fc7\u4e00\u4e2a",(0,r.kt)("inlineCode",{parentName:"p"},"logHandler"),"\u6765\u5b9e\u6218\u6f14\u793a\u4e0b\u5982\u4f55\u901a\u8fc7",(0,r.kt)("inlineCode",{parentName:"p"},"next"),"\u5feb\u901f\u5b9e\u73b0\u4e00\u4e2a\u65e5\u5fd7\u4e2d\u95f4\u4ef6~"),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="\u5168\u5c40\u6ce8\u518c" showLineNumbers {7,12}',title:'"\u5168\u5c40\u6ce8\u518c"',showLineNumbers:!0,"{7,12}":!0},'import pywss\nimport time\nimport random\n\ndef logHandler(ctx: pywss.Context):\n    startTime = time.time()\n    ctx.next()\n    cost = time.time() - startTime\n    print(f"{ctx.method} - {ctx.route} - cost: {cost: .2f}")\n\napp = pywss.App()\napp.use(logHandler)\napp.get("/hi", lambda ctx: time.sleep(random.randint(1, 3)) or ctx.write("Hi~"))\napp.post("/hello", lambda ctx: time.sleep(random.randint(1, 3)) or ctx.write("HelloWorld"))\napp.run()\n')),(0,r.kt)("pre",null,(0,r.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="\u5c40\u90e8\u6ce8\u518c" showLineNumbers {7,13}',title:'"\u5c40\u90e8\u6ce8\u518c"',showLineNumbers:!0,"{7,13}":!0},'import pywss\nimport time\nimport random\n\ndef logHandler(ctx: pywss.Context):\n    startTime = time.time()\n    ctx.next()\n    cost = time.time() - startTime\n    print(f"{ctx.method} - {ctx.route} - cost: {cost: .2f}")\n\napp = pywss.App()\napp.get("/hi", lambda ctx: time.sleep(random.randint(1, 3)) or ctx.write("Hi~"))\napp.post("/hello", logHandler, lambda ctx: time.sleep(random.randint(1, 3)) or ctx.write("HelloWorld"))\napp.run()\n')))}c.isMDXComponent=!0}}]);