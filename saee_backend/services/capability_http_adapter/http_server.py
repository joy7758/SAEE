"""Localhost-only standard-library HTTP server for Capability Runtime."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .http_request_handler import process_http_request


BIND_ADDRESS = "127.0.0.1"
MAX_BODY_BYTES = 1_000_000


class LocalCapabilityHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "SAEELocalHTTP/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(self, status: int, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(encoded)

    def _host_allowed(self) -> bool:
        host = self.headers.get("Host", "").rsplit(":", 1)[0].lower()
        return host in {"127.0.0.1", "localhost"}

    def do_POST(self) -> None:
        if not self._host_allowed():
            status, response = process_http_request(self.path, None)
            self._send(403, response)
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            status, response = process_http_request(self.path, None)
            self._send(415, response)
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            length = -1
        if length < 0:
            status, response = process_http_request(self.path, None)
            self._send(411, response)
            return
        if length > MAX_BODY_BYTES:
            status, response = process_http_request(self.path, None)
            self._send(413, response)
            return
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            body = None
        status, response = process_http_request(self.path, body)
        self._send(status, response)

    def do_GET(self) -> None:
        if not self._host_allowed():
            status, response = process_http_request(self.path, None)
            self._send(403, response)
            return
        status, response = process_http_request(self.path, None)
        self._send(405 if status != 404 else 404, response)


class LocalCapabilityHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True


def create_local_http_server(port: int = 0) -> LocalCapabilityHTTPServer:
    if not isinstance(port, int) or not 0 <= port <= 65535:
        raise ValueError("port must be an integer from 0 to 65535")
    return LocalCapabilityHTTPServer((BIND_ADDRESS, port), LocalCapabilityHTTPRequestHandler)
