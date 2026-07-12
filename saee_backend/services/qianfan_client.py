"""Minimal allowlisted Baidu Qianfan client for SAEE product validation."""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from typing import Any


QIANFAN_ENDPOINT = "https://qianfan.baidubce.com/v2/chat/completions"
QIANFAN_MODEL = "ernie-4.5-turbo-128k"
QIANFAN_KEY_ENV = "QIANFAN_API_KEY"


class QianfanProviderError(RuntimeError):
    """Fail-closed provider error that never includes a credential or response body."""

    def __init__(self, category: str, status: int | None = None) -> None:
        self.category = category
        self.status = status
        super().__init__(category)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def strip_provider_key(environment: dict[str, str] | None = None) -> dict[str, str]:
    clean = dict(os.environ if environment is None else environment)
    for key in (QIANFAN_KEY_ENV, "OPENAI_API_KEY", "BAIDU_API_KEY", "ARK_API_KEY"):
        clean.pop(key, None)
    return clean


class QianfanClient:
    def __init__(self, key: str | None = None, endpoint: str | None = None, model: str | None = None) -> None:
        self.key = key or os.environ.get(QIANFAN_KEY_ENV, "")
        if not self.key:
            raise QianfanProviderError("missing_api_key")
        self.endpoint = endpoint or QIANFAN_ENDPOINT
        if self.endpoint != QIANFAN_ENDPOINT:
            raise QianfanProviderError("endpoint_not_allowlisted")
        self.model = model or os.environ.get("QIANFAN_MODEL", QIANFAN_MODEL)
        if self.model != QIANFAN_MODEL:
            raise QianfanProviderError("model_not_allowlisted")

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], tool_choice: Any) -> dict[str, Any]:
        body = canonical_json({
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "stream": False,
        }).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "Authorization": "Bearer " + self.key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read(2_000_001)
                status = int(response.status)
        except urllib.error.HTTPError as exc:
            raise QianfanProviderError("provider_http_error", exc.code) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise QianfanProviderError("provider_timeout_or_network_error") from None
        if len(raw) > 2_000_000:
            raise QianfanProviderError("provider_response_too_large")
        if status >= 400:
            raise QianfanProviderError("provider_http_error", status)
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise QianfanProviderError("provider_non_json_response") from None
        if not isinstance(value, dict) or not isinstance(value.get("choices"), list) or not value["choices"]:
            raise QianfanProviderError("provider_invalid_completion")
        return value
