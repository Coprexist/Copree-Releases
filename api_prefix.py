"""打包版的 /api 前缀中间件（纯 ASGI）。

**只改路径，绝不把 query 拼回 path。** Starlette 按 `scope["path"]` 匹配路由，path 里一旦带上
`?limit=20`，`/gm/{group_id}/messages` 就匹配不上，请求会掉进 `/{full_path:path}` 的 SPA 兜底，
拿回 index.html（200 + text/html）。前端把 HTML 当 JSON 解失败的后果不是"接口不存在"，而是
`messages.map is not a function`——症状离现场很远。

2026-08-31 引入（`aae7ef7`）到 2026-10-27 之间的桌面版就死在这上面：登录、列表这些**不带 query**
的接口都正常，一点开对话（`/gm/{id}/messages?limit=20`）就崩，看起来像"前端坏了"。
附件下载（`/fs/download/{id}?token=...`）同理，也是那条 query。

**写成纯 ASGI 而不是 `BaseHTTPMiddleware`**：后者只接管 http，websocket 会被原样透传——
将来若有人把 WS 挪到 `/api/ws`，它会静默连不上，症状同样离现场很远。两种 scope 一视同仁。

query 本来就在 `scope["query_string"]` 里，路由与 `request.query_params` 都读得到，不必搬。
守它的是 `scripts/check_api_prefix.py`（CI 在 stage 之后跑，http + ws 都测）。
"""


class APIPrefixMiddleware:
    """移除 /api 前缀，与 vite 代理行为一致。"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            path = scope.get("path", "")
            if path.startswith("/api/"):
                scope = dict(scope)                    # 不改上游传下来的原 scope
                scope["path"] = path[4:]               # /api/auth/login → /auth/login
                raw = scope.get("raw_path")
                if raw:
                    scope["raw_path"] = raw[4:]        # 同一份路径的字节口径，别留两套
        await self.app(scope, receive, send)
