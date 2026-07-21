#!/usr/bin/env python3
"""Run SAEE validation in a tracked-only disposable repository clone.

The legacy validation graph contains smoke scripts that intentionally refresh
derived artifacts before validating them.  This module preserves those
assertions while ensuring that normal checks never write to the caller's
tracked files.  Ignored runtime output is deliberately not copied.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
ISOLATED_ENV = "SAEE_CHECK_ISOLATED"
VOLATILE_JSON_KEYS = {
    "generated_at",
    "detached_local_child_processes",
    "local_trial_started_by_manager",
}
VOLATILE_MARKDOWN_PATTERN = re.compile(
    r"^(?P<prefix>\s*(?:[-*]\s+)?)(?P<key>detached_local_child_processes|local_trial_started_by_manager):\s+.*$",
    re.MULTILINE,
)


class IsolationError(RuntimeError):
    """Raised when a disposable validation workspace cannot be prepared."""


def _git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _nul_paths(raw: bytes) -> list[Path]:
    return [Path(item.decode("utf-8")) for item in raw.split(b"\0") if item]


def _overlay_current_worktree(source: Path, sandbox: Path) -> None:
    """Overlay tracked and non-ignored untracked source files on a local clone."""
    visible = _nul_paths(
        _git(source, "ls-files", "-z", "--cached", "--others", "--exclude-standard").stdout
    )
    deleted = set(_nul_paths(_git(source, "ls-files", "-z", "--deleted").stdout))
    for relative in visible:
        source_path = source / relative
        target_path = sandbox / relative
        if relative in deleted or not source_path.exists():
            if target_path.is_dir() and not target_path.is_symlink():
                shutil.rmtree(target_path)
            else:
                target_path.unlink(missing_ok=True)
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.is_symlink():
            target_path.unlink(missing_ok=True)
            target_path.symlink_to(os.readlink(source_path))
        else:
            shutil.copy2(source_path, target_path)


def create_sandbox(source: Path, parent: Path) -> Path:
    """Create a local clone and overlay the caller's current non-ignored state."""
    sandbox = parent / "repository"
    clone = subprocess.run(
        ["git", "clone", "--quiet", "--no-hardlinks", str(source), str(sandbox)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if clone.returncode != 0:
        raise IsolationError("local clone failed: " + clone.stderr.strip())
    _overlay_current_worktree(source, sandbox)
    return sandbox


def _tracked_paths(root: Path) -> list[Path]:
    return _nul_paths(_git(root, "ls-files", "-z").stdout)


def _snapshot(root: Path) -> dict[Path, bytes | None]:
    result: dict[Path, bytes | None] = {}
    for relative in _tracked_paths(root):
        path = root / relative
        result[relative] = path.read_bytes() if path.is_file() else None
    return result


def _strip_volatile_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_volatile_json(item)
            for key, item in value.items()
            if key not in VOLATILE_JSON_KEYS
        }
    if isinstance(value, list):
        return [_strip_volatile_json(item) for item in value]
    return value


def normalize_generated(relative: Path, raw: bytes | None) -> bytes | None:
    """Normalize declared runtime metadata while preserving substantive content."""
    if raw is None:
        return None
    if relative.suffix == ".json":
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return raw
        canonical = json.dumps(
            _strip_volatile_json(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return (canonical + "\n").encode("utf-8")
    if relative.suffix in {".md", ".txt"}:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw
        text = VOLATILE_MARKDOWN_PATTERN.sub(
            lambda match: f"{match.group('prefix')}{match.group('key')}: <runtime-state>",
            text,
        )
        return text.encode("utf-8")
    return raw


def generated_differences(
    before: dict[Path, bytes | None], after: dict[Path, bytes | None]
) -> tuple[list[Path], list[Path]]:
    raw_changes: list[Path] = []
    substantive: list[Path] = []
    for relative in sorted(set(before) | set(after), key=lambda item: item.as_posix()):
        old = before.get(relative)
        new = after.get(relative)
        if old == new:
            continue
        raw_changes.append(relative)
        if normalize_generated(relative, old) != normalize_generated(relative, new):
            substantive.append(relative)
    return raw_changes, substantive


def _isolated_environment(sandbox: Path) -> dict[str, str]:
    env = os.environ.copy()
    env[ISOLATED_ENV] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["TZ"] = "UTC"
    env["LC_ALL"] = "C"
    env["SAEE_PROVIDER_EVIDENCE_MODE"] = "optional"
    env["SAEE_CHECK_SANDBOX"] = str(sandbox)
    return env


def _emit_stable_output(data: str, sandbox: Path, stream) -> None:
    stream.write(data.replace(str(sandbox), "<SAEE_CHECK_SANDBOX>"))


def run_isolated(
    command: Sequence[str],
    *,
    source: Path = ROOT,
    compare_generated: bool = False,
) -> int:
    """Run a command in a clean clone containing no ignored source artifacts."""
    with tempfile.TemporaryDirectory(prefix="saee-check-") as directory:
        sandbox = create_sandbox(source, Path(directory))
        before = _snapshot(sandbox) if compare_generated else {}
        result = subprocess.run(
            list(command),
            cwd=sandbox,
            env=_isolated_environment(sandbox),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _emit_stable_output(result.stdout, sandbox, sys.stdout)
        _emit_stable_output(result.stderr, sandbox, sys.stderr)
        if result.returncode != 0:
            return result.returncode
        if compare_generated:
            after = _snapshot(sandbox)
            raw_changes, substantive = generated_differences(before, after)
            if substantive:
                print("CHECK_GENERATED: FAIL substantive_generated_differences=" + str(len(substantive)))
                for relative in substantive:
                    print("CHECK_GENERATED_DIFFERENCE=" + relative.as_posix())
                return 1
            print(
                "CHECK_GENERATED: PASS "
                f"raw_generated_changes={len(raw_changes)} normalized_differences=0 "
                "volatile_runtime_metadata_excluded=true"
            )
        return 0


def run_mainline_readonly(source: Path = ROOT) -> int:
    return run_isolated([sys.executable, "scripts/mainline_guard.py"], source=source)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "check-generated", "mainline"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if os.environ.get(ISOLATED_ENV) == "1":
        raise IsolationError("nested check isolation is not allowed")
    if args.mode == "check":
        return run_isolated(["make", "check-in-place"])
    if args.mode == "check-generated":
        return run_isolated(["make", "generate"], compare_generated=True)
    return run_mainline_readonly()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IsolationError as exc:
        raise SystemExit("SAEE_CHECK_ISOLATION: FAIL " + str(exc)) from exc
