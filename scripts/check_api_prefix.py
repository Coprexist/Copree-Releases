"""守住打包版的 /api 前缀中间件：带 query 的请求必须命中真实路由。

这条中间件**只存在于打包版**（vite dev 由代理改写路径，主仓 844 条用例一条都碰不到它）。
它一旦把 query 拼进 `scope["path"]`，路由就匹配不上，请求会掉进 SPA 兜底、拿回 index.html；
前端把 HTML 当 JSON 解失败后拿到空对象，症状是「点开对话就崩：messages.map is not a function」——
2026-08-31 引入到 2026-10-27 的桌面版就死在这里，登录和列表（不带 query）却一切正常。

它还必须覆盖 **websocket** scope：BaseHTTPMiddleware 只接管 http，WS 会被原样透传，
将来谁把 WS 挪到 /api/ws 就是"连不上、也看不出为什么"。

跑法（CI 在 stage 之后跑一次）：
    python scripts/check_api_prefix.py
"""
import os
import sys

# Windows 的 CI 控制台是 cp1252，直接 print 中文会 UnicodeEncodeError 把构建搞挂
# （2026-10-27 v0.4.15 首跑就挂在这——守卫本身是通过的，死在了打日志上）。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001 — 老环境没有 reconfigure 就算了，别因此中断
        pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.testclient import TestClient

from api_prefix import APIPrefixMiddleware


def build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/gm/{group_id}/messages")
    async def messages(group_id: int, limit: int = 20, after_id: int | None = None):
        # 形状对齐真实的 /gm/{id}/messages：它**永远带 query**（limit/before_id/after_id）
        return JSONResponse([{"id": 1, "group_id": group_id, "limit": limit, "after_id": after_id}])

    @app.websocket("/ws")
    async def ws_endpoint(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("hi")
        await websocket.close()

    @app.get("/{full_path:path}")
    async def spa(full_path: str):
        # 与 server_core.py 的兜底同形：任何没命中的路径都返回首页 HTML
        return HTMLResponse("<!doctype html><html><body>SPA</body></html>")

    app.add_middleware(APIPrefixMiddleware)
    return app


def body_json(res):
    """解析 JSON；解析不出来就是 None——守卫本身不能因为被测对象坏了而崩掉。"""
    try:
        return res.json()
    except Exception:  # noqa: BLE001 — 拿到 HTML 就必然走到这里
        return None


def main() -> int:
    client = TestClient(build_app())
    failures: list[str] = []

    def check(label: str, ok: bool, detail="") -> None:
        print(("  OK   " if ok else "  FAIL ") + label + ("" if ok else " :: " + str(detail)))
        if not ok:
            failures.append(label)

    # ① 核心：带 query 的 API 必须拿到 JSON —— 桌面版"点开对话"发的就是这一条
    res = client.get("/api/gm/7/messages?limit=20&after_id=5")
    check("带 query 的 /api 请求返回 JSON",
          res.headers.get("content-type", "").startswith("application/json"),
          res.headers.get("content-type"))
    check("带 query 的请求命中了真实路由",
          res.status_code == 200
          and body_json(res) == [{"id": 1, "group_id": 7, "limit": 20, "after_id": 5}],
          res.text[:120])

    # ② 不带 query 的老路径不许退化
    res = client.get("/api/gm/7/messages")
    check("不带 query 的 /api 请求仍返回 JSON",
          res.headers.get("content-type", "").startswith("application/json"), res.text[:80])

    # ③ /api 前缀确实被摘掉：未知路径落到 SPA，而不是去找 /api/...
    res = client.get("/api/nope/no-route")
    check("/api 下的未知路径仍由 SPA 兜底（说明前缀已摘）",
          res.status_code == 200 and "SPA" in res.text, res.status_code)

    # ④ 非 /api 的 SPA 路由不受影响
    res = client.get("/dm/9")
    check("非 /api 路径仍走 SPA", res.status_code == 200 and "SPA" in res.text, res.status_code)

    # ⑤ websocket 的 scope 也要摘前缀（BaseHTTPMiddleware 会漏掉这一类）
    try:
        with client.websocket_connect("/api/ws?token=x") as ws:
            check("带 query 的 /api websocket 能连上", ws.receive_text() == "hi")
    except Exception as exc:                      # noqa: BLE001 — 连不上就是失败，原因打出来
        check("带 query 的 /api websocket 能连上", False, repr(exc)[:160])

    print()
    if failures:
        print("FAILED: " + "；".join(failures))
        return 1
    print("api prefix ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
