#!/usr/bin/env python3
"""One-use loopback-only browser form for securely storing ARK_API_KEY."""

from __future__ import annotations

import html
import secrets
import sys
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_store_ark_key import ENV_FILE, store_key


TOKEN = secrets.token_urlsafe(32)
MAX_BODY = 8192


def page(body: str) -> bytes:
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAEE 火山 Key 本地写入</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;background:#f5f7fb;color:#172033;margin:0}}main{{max-width:620px;margin:10vh auto;background:white;padding:32px;border-radius:16px;box-shadow:0 12px 40px #1a2b4a1a}}h1{{font-size:24px}}label{{display:block;margin:24px 0 8px}}input{{box-sizing:border-box;width:100%;padding:14px;border:1px solid #9aa7bd;border-radius:8px;font-size:16px}}button{{margin-top:18px;padding:12px 22px;border:0;border-radius:8px;background:#155eef;color:white;font-size:16px}}.note{{color:#526175;line-height:1.7}}code{{background:#eef2f8;padding:2px 5px;border-radius:4px}}</style></head>
<body><main>{body}</main></body></html>""".encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    server_version = "SAEEKeyStore/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def headers_common(self) -> None:
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")

    def respond(self, status: int, body: str) -> None:
        payload = page(body)
        self.send_response(status)
        self.headers_common()
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        if query.get("token") != [TOKEN]:
            self.respond(403, "<h1>访问被拒绝</h1>")
            return
        self.respond(200, f"""<h1>写入火山方舟 API Key</h1>
<p class="note">此页面仅运行在本机 <code>127.0.0.1</code>，提交后原子写入 <code>.env.local</code>。Key 不回显、不写日志、不发送到互联网。</p>
<form method="post" action="/store"><input type="hidden" name="token" value="{html.escape(TOKEN)}">
<label for="key">ARK_API_KEY</label><input id="key" name="key" type="password" required minlength="20" autocomplete="off" autofocus>
<button type="submit">安全写入</button></form>""")

    def do_POST(self) -> None:
        if self.path != "/store":
            self.respond(404, "<h1>未找到</h1>")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            self.respond(400, "<h1>输入无效</h1>")
            return
        form = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        if form.get("token") != [TOKEN]:
            self.respond(403, "<h1>请求校验失败</h1>")
            return
        try:
            store_key(form.get("key", [""])[0])
        except ValueError:
            self.respond(400, "<h1>Key 格式无效</h1><p>请关闭本页后重新启动写入程序。</p>")
            return
        self.respond(200, f"<h1>写入成功</h1><p class='note'>已安全保存到 <code>{html.escape(str(ENV_FILE))}</code>，权限为 <code>600</code>。可以关闭此页面。</p>")
        threading.Thread(target=self.server.shutdown, daemon=True).start()


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/?token={TOKEN}"
    print("SAEE_ARK_KEY_LOCAL_FORM: READY", flush=True)
    print(f"url={url}", flush=True)
    print("network_scope=loopback_only", flush=True)
    print("secret_logged=false", flush=True)
    webbrowser.open(url, new=1)
    server.serve_forever(poll_interval=0.2)
    server.server_close()
    print("SAEE_ARK_KEY_LOCAL_FORM: STORED_AND_CLOSED", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
