#!/usr/bin/env python3
"""Manage a local SAEE trial session.

This script starts, stops, describes, or checks the local MVP trial session
only. It does not install dependencies, open a browser, call external services,
modify product behavior, touch private core, or claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
LANDING_DIR = ROOT / "phase_b_product/landing"
RUNTIME_DIR = ROOT / ".saee_runtime"
SESSION_PATH = RUNTIME_DIR / "local_trial_session.json"
BACKEND_LOG = RUNTIME_DIR / "local_trial_backend.log"
LANDING_LOG = RUNTIME_DIR / "local_trial_landing.log"
LOCAL_VENV_PYTHON = ROOT / ".venv/bin/python"


def boundary_flags() -> dict[str, bool]:
    return {
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_data_allowed": False,
        "paid_trial_enabled": False,
        "payment_provider_configured": False,
        "product_launched": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "external_calls_made": False,
        "browser_opened_by_script": False,
        "dependencies_installed_by_script": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
    }


def default_python() -> str:
    if LOCAL_VENV_PYTHON.exists():
        return str(LOCAL_VENV_PYTHON)
    return sys.executable


def selected_python_source(python: str) -> str:
    try:
        if Path(python).resolve() == LOCAL_VENV_PYTHON.resolve():
            return "local_venv"
    except OSError:
        pass
    return "explicit_or_current_python"


def describe_payload() -> dict[str, Any]:
    python = default_python()
    boundaries = boundary_flags()
    return {
        "local_trial_session_manager_v0_1": True,
        "session_scope": "local_controlled_trial_demo_operator_tool",
        "status": "available",
        "commands": ["describe", "preflight", "status", "start", "stop"],
        "default_python": python,
        "default_python_source": selected_python_source(python),
        "prefers_local_venv_python": True,
        "detached_local_child_processes": True,
        "preflight": {
            "scope": "local_controlled_trial_demo_operator_check",
            "command_template": (
                "python3 scripts/saee_local_trial_session.py --json preflight"
            ),
            "checks": [
                "required local files",
                "selected Python executable",
                "FastAPI and Uvicorn import availability",
                "backend port ownership",
                "landing port ownership",
            ],
        },
        "backend": {
            "default_host": "127.0.0.1",
            "default_port": 8000,
            "health_url": "http://127.0.0.1:8000/health",
            "demo_endpoint": "http://127.0.0.1:8000/experiment/run",
            "command_template": (
                f"{python} -m uvicorn saee_backend.main:app --host 127.0.0.1 --port 8000"
            ),
        },
        "landing": {
            "default_host": "127.0.0.1",
            "default_port": 8765,
            "url": "http://127.0.0.1:8765/",
            "directory": "phase_b_product/landing",
            "command_template": "python -m http.server 8765 --bind 127.0.0.1",
        },
        "runtime_files": {
            "session": str(SESSION_PATH.relative_to(ROOT)),
            "backend_log": str(BACKEND_LOG.relative_to(ROOT)),
            "landing_log": str(LANDING_LOG.relative_to(ROOT)),
        },
        "boundaries": boundaries,
        **boundaries,
        "next_human_action": (
            "Run start, open http://127.0.0.1:8765/ manually, click Run Demo Battle, "
            "then run stop when finished."
        ),
    }


def require_local_paths() -> None:
    if not (ROOT / "saee_backend/main.py").exists():
        raise SystemExit("SAEE_LOCAL_TRIAL_SESSION: FAIL: missing saee_backend/main.py")
    if not (LANDING_DIR / "index.html").exists():
        raise SystemExit("SAEE_LOCAL_TRIAL_SESSION: FAIL: missing landing index.html")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def process_running(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def port_open(host: str, port: int, timeout: float = 0.35) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def python_module_available(python: str, module: str) -> bool:
    code = (
        "import importlib.util, sys; "
        f"sys.exit(0 if importlib.util.find_spec({module!r}) else 1)"
    )
    try:
        result = subprocess.run(
            [python, "-c", code],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def fetch_text(url: str, timeout: float = 1.5) -> tuple[bool, str]:
    req = Request(url, headers={"User-Agent": "saee-local-trial-session/0.1"})
    try:
        with urlopen(req, timeout=timeout) as response:
            return True, response.read(2000).decode("utf-8", errors="replace")
    except (OSError, URLError):
        return False, ""


def wait_for(url: str, expected: str, timeout_seconds: float) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        ok, text = fetch_text(url)
        if ok and expected in text:
            return True
        time.sleep(0.25)
    return False


def preflight_payload(python: str, backend_port: int, landing_port: int) -> dict[str, Any]:
    boundaries = boundary_flags()
    backend_url = f"http://127.0.0.1:{backend_port}/health"
    landing_url = f"http://127.0.0.1:{landing_port}/"
    backend_ok, backend_text = fetch_text(backend_url)
    landing_ok, landing_text = fetch_text(landing_url)
    required_files = {
        "backend_entrypoint": (ROOT / "saee_backend/main.py").exists(),
        "backend_requirements": (ROOT / "saee_backend/requirements.txt").exists(),
        "landing_index": (LANDING_DIR / "index.html").exists(),
        "landing_app": (LANDING_DIR / "app.js").exists(),
    }
    fastapi_available = python_module_available(python, "fastapi")
    uvicorn_available = python_module_available(python, "uvicorn")
    backend_port_open = port_open("127.0.0.1", backend_port)
    landing_port_open = port_open("127.0.0.1", landing_port)
    backend_owned_by_saee = backend_ok and '"ok"' in backend_text
    landing_owned_by_saee = landing_ok and "SAEE" in landing_text
    backend_port_usable = (not backend_port_open) or backend_owned_by_saee
    landing_port_usable = (not landing_port_open) or landing_owned_by_saee
    dependency_ready = backend_owned_by_saee or (fastapi_available and uvicorn_available)
    required_files_present = all(required_files.values())
    ready_to_start = (
        required_files_present
        and dependency_ready
        and backend_port_usable
        and landing_port_usable
    )
    missing = [name for name, present in required_files.items() if not present]
    if not dependency_ready and not fastapi_available:
        missing.append("python_module_fastapi")
    if not dependency_ready and not uvicorn_available:
        missing.append("python_module_uvicorn")
    if backend_port_open and not backend_owned_by_saee:
        missing.append(f"backend_port_{backend_port}_occupied_by_unknown_service")
    if landing_port_open and not landing_owned_by_saee:
        missing.append(f"landing_port_{landing_port}_occupied_by_unknown_service")
    return {
        "local_trial_session_manager_v0_1": True,
        "local_trial_session_preflight_v0_1": True,
        "preflight_scope": "local_controlled_trial_demo_operator_check",
        "status": "pass" if ready_to_start else "hold",
        "ready_to_start": ready_to_start,
        "selected_python": python,
        "selected_python_source": selected_python_source(python),
        "prefers_local_venv_python": True,
        "required_files_present": required_files_present,
        "required_files": required_files,
        "fastapi_available": fastapi_available,
        "uvicorn_available": uvicorn_available,
        "backend_port": backend_port,
        "landing_port": landing_port,
        "backend_port_open": backend_port_open,
        "landing_port_open": landing_port_open,
        "backend_owned_by_saee": backend_owned_by_saee,
        "landing_owned_by_saee": landing_owned_by_saee,
        "backend_port_usable": backend_port_usable,
        "landing_port_usable": landing_port_usable,
        "missing_or_blocking_items": missing,
        "next_human_action": (
            "Run start if status is pass; otherwise prepare the selected local Python "
            "environment or choose unused local ports, then rerun preflight."
        ),
        "boundaries": boundaries,
        **boundaries,
    }


def status_payload(backend_port: int, landing_port: int) -> dict[str, Any]:
    boundaries = boundary_flags()
    session = read_json(SESSION_PATH)
    backend_url = f"http://127.0.0.1:{backend_port}/health"
    landing_url = f"http://127.0.0.1:{landing_port}/"
    backend_ok, backend_text = fetch_text(backend_url)
    landing_ok, landing_text = fetch_text(landing_url)
    backend_pid = session.get("backend_pid")
    landing_pid = session.get("landing_pid")
    if isinstance(backend_pid, str) and backend_pid.isdigit():
        backend_pid = int(backend_pid)
    if isinstance(landing_pid, str) and landing_pid.isdigit():
        landing_pid = int(landing_pid)
    return {
        "local_trial_session_manager_v0_1": True,
        "session_state": "running" if backend_ok and landing_ok else "not_running",
        "backend_health_ok": backend_ok and '"ok"' in backend_text,
        "landing_page_ok": landing_ok and "SAEE" in landing_text,
        "backend_url": backend_url,
        "landing_url": landing_url,
        "session_file_exists": SESSION_PATH.exists(),
        "backend_pid": backend_pid,
        "landing_pid": landing_pid,
        "backend_pid_running": process_running(backend_pid if isinstance(backend_pid, int) else None),
        "landing_pid_running": process_running(landing_pid if isinstance(landing_pid, int) else None),
        "started_by_manager": session.get("started_by_manager") is True,
        "detached_local_child_processes": session.get("detached_local_child_processes") is True,
        "boundaries": boundaries,
        **boundaries,
    }


def open_log(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path.open("ab")


def start(args: argparse.Namespace) -> dict[str, Any]:
    require_local_paths()
    preflight = preflight_payload(args.python, args.backend_port, args.landing_port)
    if not preflight["ready_to_start"]:
        raise SystemExit(
            "SAEE_LOCAL_TRIAL_SESSION: FAIL: local preflight did not pass. "
            "Run `python3 scripts/saee_local_trial_session.py --json preflight`."
        )
    backend_url = f"http://127.0.0.1:{args.backend_port}/health"
    landing_url = f"http://127.0.0.1:{args.landing_port}/"
    backend_already = wait_for(backend_url, '"ok"', 0.5)
    landing_already = wait_for(landing_url, "SAEE", 0.5)
    backend_proc: subprocess.Popen[bytes] | None = None
    landing_proc: subprocess.Popen[bytes] | None = None

    if not backend_already:
        backend_log = open_log(BACKEND_LOG)
        backend_proc = subprocess.Popen(
            [
                args.python,
                "-m",
                "uvicorn",
                "saee_backend.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(args.backend_port),
            ],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=backend_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        backend_log.close()

    if not landing_already:
        landing_log = open_log(LANDING_LOG)
        landing_proc = subprocess.Popen(
            [
                args.python,
                "-m",
                "http.server",
                str(args.landing_port),
                "--bind",
                "127.0.0.1",
            ],
            cwd=LANDING_DIR,
            stdin=subprocess.DEVNULL,
            stdout=landing_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        landing_log.close()

    backend_ok = wait_for(backend_url, '"ok"', args.wait_seconds)
    landing_ok = wait_for(landing_url, "SAEE", args.wait_seconds)
    if not (backend_ok and landing_ok):
        for proc in (backend_proc, landing_proc):
            if proc and proc.poll() is None:
                proc.terminate()
        raise SystemExit(
            "SAEE_LOCAL_TRIAL_SESSION: FAIL: local session did not become ready. "
            f"Check {BACKEND_LOG} and {LANDING_LOG}."
        )

    session = {
        "local_trial_session_manager_v0_1": True,
        "session_state": "running",
        "started_by_manager": True,
        "backend_already_running": backend_already,
        "landing_already_running": landing_already,
        "backend_pid": backend_proc.pid if backend_proc else None,
        "landing_pid": landing_proc.pid if landing_proc else None,
        "backend_url": backend_url,
        "landing_url": landing_url,
        "demo_url": landing_url,
        "browser_opened_by_script": False,
        "external_calls_made": False,
        "detached_local_child_processes": True,
        "boundaries": boundary_flags(),
    }
    session.update(session["boundaries"])
    write_json(SESSION_PATH, session)
    return session


def stop(_: argparse.Namespace) -> dict[str, Any]:
    session = read_json(SESSION_PATH)
    stopped: list[str] = []
    skipped: list[str] = []
    for label in ("backend", "landing"):
        pid = session.get(f"{label}_pid")
        if isinstance(pid, str) and pid.isdigit():
            pid = int(pid)
        if not isinstance(pid, int) or pid <= 0:
            skipped.append(label)
            continue
        if process_running(pid):
            os.kill(pid, signal.SIGTERM)
            stopped.append(label)
        else:
            skipped.append(label)
    result = {
        "local_trial_session_manager_v0_1": True,
        "session_state": "stopped",
        "stopped": stopped,
        "skipped": skipped,
        "external_calls_made": False,
        "browser_opened_by_script": False,
        "boundaries": boundary_flags(),
    }
    result.update(result["boundaries"])
    write_json(SESSION_PATH, result)
    return result


def print_payload(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print("SAEE_LOCAL_TRIAL_SESSION")
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            print(f"{key}: {value}")
    if "landing_url" in payload:
        print(f"Open manually: {payload['landing_url']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the local SAEE trial session.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("describe", help="Describe the local trial session manager.")
    status_parser = sub.add_parser("status", help="Check local trial session status.")
    status_parser.add_argument("--backend-port", type=int, default=8000)
    status_parser.add_argument("--landing-port", type=int, default=8765)
    preflight_parser = sub.add_parser(
        "preflight", help="Check whether the local trial session can be started."
    )
    preflight_parser.add_argument("--python", default=default_python())
    preflight_parser.add_argument("--backend-port", type=int, default=8000)
    preflight_parser.add_argument("--landing-port", type=int, default=8765)
    start_parser = sub.add_parser("start", help="Start backend and landing page locally.")
    start_parser.add_argument("--python", default=default_python())
    start_parser.add_argument("--backend-port", type=int, default=8000)
    start_parser.add_argument("--landing-port", type=int, default=8765)
    start_parser.add_argument("--wait-seconds", type=float, default=20.0)
    sub.add_parser("stop", help="Stop processes started by this manager.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "describe":
        payload = describe_payload()
    elif args.command == "preflight":
        payload = preflight_payload(args.python, args.backend_port, args.landing_port)
    elif args.command == "status":
        payload = status_payload(args.backend_port, args.landing_port)
    elif args.command == "start":
        payload = start(args)
    elif args.command == "stop":
        payload = stop(args)
    else:
        raise SystemExit(f"unsupported command: {args.command}")
    print_payload(payload, args.json)


if __name__ == "__main__":
    main()
