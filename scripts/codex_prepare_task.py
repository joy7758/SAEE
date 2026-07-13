#!/usr/bin/env python3
"""Prepare a compact SAEE Codex task summary from local context files.

This script reads only local files. It does not call external services, execute
SAEE runtime, or modify product behavior.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_DIR = ROOT / ".codex"


def read_text(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def first_nonempty_lines(text: str, limit: int = 12) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lines.append(line)
        if len(lines) >= limit:
            break
    return lines


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}:\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+.+?:\s*$", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def normalize_task_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    try:
        path.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit("task file must be inside the SAEE repository") from exc
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a compact SAEE Codex task summary.")
    parser.add_argument("task_file", help="Task markdown file, usually under .codex/task_queue/")
    args = parser.parse_args()

    task_path = normalize_task_path(args.task_file)
    task = read_text(task_path)
    context = read_text(CODEX_DIR / "context.md")
    current_state = read_text(CODEX_DIR / "current_state.md")
    rules = read_text(CODEX_DIR / "rules.md")
    validation = read_text(CODEX_DIR / "validation_commands.md")

    sections = {
        "Objective": extract_section(task, "Objective"),
        "Files allowed to modify": extract_section(task, "Files allowed to modify"),
        "Files forbidden": extract_section(task, "Files forbidden"),
        "Expected output": extract_section(task, "Expected output"),
        "Validation command": extract_section(task, "Validation command"),
        "Boundary": extract_section(task, "Boundary"),
    }

    print("# SAEE Codex Task Summary")
    print()
    print(f"Task file: `{task_path.relative_to(ROOT)}`")
    print()
    print("## Context")
    for line in first_nonempty_lines(context, 10):
        print(f"- {line}")
    print()
    print("## Current State")
    for line in first_nonempty_lines(current_state, 12):
        print(f"- {line}")
    print()
    print("## Task Scope")
    for key, value in sections.items():
        print(f"### {key}")
        print(value or "(not specified)")
        print()
    print("## Required Rules")
    for line in first_nonempty_lines(rules, 12):
        print(f"- {line}")
    print()
    print("## Validation")
    specific = sections.get("Validation command") or ""
    print(specific.strip() or "\n".join(first_nonempty_lines(validation, 8)))


if __name__ == "__main__":
    main()
