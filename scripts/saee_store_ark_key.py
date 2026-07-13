#!/usr/bin/env python3
"""Securely store ARK_API_KEY in the repository-local ignored env file."""

from __future__ import annotations

import getpass
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env.local"
KEY_NAME = "ARK_API_KEY"


def store_key(value: str) -> None:
    value = value.strip()
    if not value:
        raise ValueError("ARK_API_KEY_EMPTY")
    if "\n" in value or "\r" in value or "\x00" in value or len(value) < 20:
        raise ValueError("ARK_API_KEY_INVALID_FORMAT")

    existing = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    preserved = [line for line in existing if not line.startswith(f"{KEY_NAME}=")]
    content = "\n".join([*preserved, f"{KEY_NAME}={value}"]).rstrip("\n") + "\n"

    ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".env.local.", dir=ENV_FILE.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, ENV_FILE)
        os.chmod(ENV_FILE, 0o600)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)

    value = ""


def main() -> int:
    value = getpass.getpass("请粘贴火山方舟 ARK_API_KEY（输入不会回显），然后按回车：")
    try:
        store_key(value)
    except ValueError as exc:
        print(f"ARK_API_KEY_STORE: REJECTED {exc}")
        return 2
    print("ARK_API_KEY_STORE: STORED")
    print(f"target={ENV_FILE}")
    print("secret_reflected=false")
    print("permissions=600")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
