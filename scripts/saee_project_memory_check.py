#!/usr/bin/env python3
"""Validate the SAEE Project Memory governance surface without changing state."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMORY_DIR = ROOT / "governance" / "project-memory"
GOVERNANCE_README = ROOT / "governance" / "README.md"

REQUIRED_FILES = (
    "README.md",
    "current-state.md",
    "frozen-decisions.md",
    "active-questions.md",
    "rejected-options.md",
    "decision-log.md",
    "memory-policy.md",
    "v2-transition-decisions.md",
)

REQUIRED_FROZEN_IDS = {f"F-{number:03d}" for number in range(1, 6)}
REQUIRED_ACTIVE_IDS = {f"Q-{number:03d}" for number in range(1, 4)}
REQUIRED_ACTIVE_V2_IDS = {"Q-V2-002"}
REQUIRED_REJECTED_IDS = {f"R-{number:03d}" for number in range(1, 5)}
REQUIRED_DECISION_IDS = {f"D-{number:03d}" for number in range(1, 7)}
REQUIRED_V2_DECISION_IDS = {f"V2-F-{number:03d}" for number in range(1, 6)}
REQUIRED_V2_PRINCIPLE_IDS = {f"V2-P-{number:03d}" for number in range(1, 4)}
APPROVED_DESIGN_DIRECTION = "APPROVED_DESIGN_DIRECTION"
FIELD_LABELS = {
    "标题：",
    "主题：",
    "状态：",
    "决定：",
    "问题：",
    "阻塞：",
    "条件：",
    "方案：",
    "原因：",
    "适用范围：",
    "权威依据：",
    "日期：",
    "证据：",
    "批准证据：",
    "边界：",
    "Human Confirmation：",
    "禁止重新讨论：",
    "下一证据：",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sections(text: str, prefix: str) -> dict[str, str]:
    pattern = re.compile(rf"^## ({re.escape(prefix)}-\d{{3}})\s*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result[match.group(1)] = text[match.end() : end]
    return result


def field_value(section: str, label: str) -> str | None:
    lines = section.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == label)
    except StopIteration:
        return None
    for line in lines[start + 1 :]:
        value = line.strip()
        if not value:
            continue
        if value.startswith("```"):
            continue
        if value == "---" or value.startswith("## ") or value in FIELD_LABELS:
            return None
        return value
    return None


def validate_frozen_text(text: str) -> list[str]:
    errors: list[str] = []
    entries = sections(text, "F")
    if set(entries) != REQUIRED_FROZEN_IDS:
        errors.append(
            f"frozen decision ids must be {sorted(REQUIRED_FROZEN_IDS)}, "
            f"found {sorted(entries)}"
        )
    for decision_id, section in entries.items():
        topic = field_value(section, "主题：")
        status = field_value(section, "状态：")
        decision = field_value(section, "决定：")
        if not topic:
            errors.append(f"{decision_id} has empty or missing 主题")
        if status != "FROZEN":
            errors.append(f"{decision_id} status must be FROZEN")
        if not decision:
            errors.append(f"{decision_id} has empty or missing 决定")
    return errors


def validate_id_set(
    text: str,
    prefix: str,
    expected: set[str],
    required_fields: tuple[str, ...],
) -> list[str]:
    errors: list[str] = []
    entries = sections(text, prefix)
    if set(entries) != expected:
        errors.append(
            f"{prefix} ids must be {sorted(expected)}, found {sorted(entries)}"
        )
    for entry_id, section in entries.items():
        for label in required_fields:
            if not field_value(section, label):
                errors.append(f"{entry_id} has empty or missing {label}")
    return errors


def validate_v2_transition_text(text: str) -> list[str]:
    errors: list[str] = []
    for marker in (
        "record_type=approved_transition_design_directions",
        "current_authority=SAEE_Development_Constitution_v1.1",
        "decision_status=APPROVED_DESIGN_DIRECTION",
        "human_confirmation=CONFIRMED",
        "approval_evidence_status=RECORDED",
        "authority_changed=false",
        "constitution_changed=false",
        "ACTIVE_AUTHORITY_CREATED=false",
    ):
        if marker not in text:
            errors.append(f"v2-transition-decisions.md missing marker: {marker}")

    decisions = sections(text, "V2-F")
    if set(decisions) != REQUIRED_V2_DECISION_IDS:
        errors.append(
            "V2-F ids must be "
            f"{sorted(REQUIRED_V2_DECISION_IDS)}, found {sorted(decisions)}"
        )
    for decision_id, section in decisions.items():
        if not field_value(section, "标题："):
            errors.append(f"{decision_id} has empty or missing 标题")
        status = field_value(section, "状态：")
        if status != APPROVED_DESIGN_DIRECTION:
            errors.append(
                f"{decision_id} status must be {APPROVED_DESIGN_DIRECTION}, "
                f"found {status}"
            )
        confirmation = field_value(section, "Human Confirmation：")
        if confirmation != "CONFIRMED":
            errors.append(
                f"{decision_id} Human Confirmation must be CONFIRMED, "
                f"found {confirmation}"
            )

    principles = sections(text, "V2-P")
    if set(principles) != REQUIRED_V2_PRINCIPLE_IDS:
        errors.append(
            "V2-P ids must be "
            f"{sorted(REQUIRED_V2_PRINCIPLE_IDS)}, found {sorted(principles)}"
        )
    for principle_id, section in principles.items():
        if not field_value(section, "标题："):
            errors.append(f"{principle_id} has empty or missing 标题")
        status = field_value(section, "状态：")
        if status != APPROVED_DESIGN_DIRECTION:
            errors.append(
                f"{principle_id} status must be {APPROVED_DESIGN_DIRECTION}, "
                f"found {status}"
            )
        if not field_value(section, "批准证据："):
            errors.append(f"{principle_id} has empty or missing 批准证据")

    return errors


def validate_v2_question_alignment(active_text: str, decision_text: str) -> list[str]:
    errors: list[str] = []
    active_entries = sections(active_text, "Q-V2")
    if set(active_entries) != REQUIRED_ACTIVE_V2_IDS:
        errors.append(
            "active Q-V2 ids must be "
            f"{sorted(REQUIRED_ACTIVE_V2_IDS)}, found {sorted(active_entries)}"
        )
    if "Q-V2-001" in active_entries:
        errors.append("Q-V2-001 must be removed from active questions after resolution")
    q_v2_002 = active_entries.get("Q-V2-002")
    if q_v2_002 is not None:
        if not field_value(q_v2_002, "问题："):
            errors.append("Q-V2-002 has empty or missing 问题")
        status = field_value(q_v2_002, "状态：")
        if status != "BLOCKED":
            errors.append(f"Q-V2-002 status must be BLOCKED, found {status}")

    d_006 = sections(decision_text, "D").get("D-006")
    if d_006 is None:
        errors.append("decision-log.md missing D-006 V2 alignment receipt")
    else:
        status = field_value(d_006, "状态：")
        if status != APPROVED_DESIGN_DIRECTION:
            errors.append(
                f"D-006 status must be {APPROVED_DESIGN_DIRECTION}, found {status}"
            )
        for marker in (
            *sorted(REQUIRED_V2_DECISION_IDS),
            *sorted(REQUIRED_V2_PRINCIPLE_IDS),
            "question_id=Q-V2-001",
            "resolution_status=RESOLVED_BY_HUMAN_DESIGN_APPROVAL",
            "active_authority=false",
        ):
            if marker not in d_006:
                errors.append(f"D-006 missing V2 alignment marker: {marker}")

    return errors


def validate_project_memory(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    memory_dir = root / "governance" / "project-memory"
    governance_readme = root / "governance" / "README.md"

    if not memory_dir.is_dir():
        return ["governance/project-memory directory is missing"]

    missing = [name for name in REQUIRED_FILES if not (memory_dir / name).is_file()]
    if missing:
        errors.append(f"missing project-memory files: {missing}")
        return errors

    documents = {name: read_text(memory_dir / name) for name in REQUIRED_FILES}
    for name, text in documents.items():
        if not text.strip():
            errors.append(f"{name} is empty")

    errors.extend(validate_frozen_text(documents["frozen-decisions.md"]))
    errors.extend(
        validate_id_set(
            documents["active-questions.md"],
            "Q",
            REQUIRED_ACTIVE_IDS,
            ("问题：", "状态："),
        )
    )
    errors.extend(
        validate_id_set(
            documents["rejected-options.md"],
            "R",
            REQUIRED_REJECTED_IDS,
            ("方案：", "状态：", "原因："),
        )
    )
    errors.extend(
        validate_id_set(
            documents["decision-log.md"],
            "D",
            REQUIRED_DECISION_IDS,
            ("日期：", "主题：", "决定：", "状态："),
        )
    )
    errors.extend(validate_v2_transition_text(documents["v2-transition-decisions.md"]))
    errors.extend(
        validate_v2_question_alignment(
            documents["active-questions.md"], documents["decision-log.md"]
        )
    )

    current_state = documents["current-state.md"]
    for marker in (
        "Phase 0.5 Stabilization",
        "PHASE_0_5_STABILIZATION",
        "phase0_5_2_status=BLOCKED",
        "phase1_authorized=false",
        "COMMIT_AUTHORIZATION=NO",
        "current_authority=SAEE_Development_Constitution_v1.1",
        "v2_design_direction_status=APPROVED_DESIGN_DIRECTION",
        "v2_authority_status=INACTIVE",
        "g1_effective=false",
        "phase_0_5_7a_authorized=false",
        "authority_switch_executed=false",
    ):
        if marker not in current_state:
            errors.append(f"current-state.md missing marker: {marker}")

    policy = documents["memory-policy.md"]
    for marker in (
        "Decision Change Proposal",
        "AI 不得自行解除冻结",
        "AI 不得把推断升级为事实",
        "capability-package/manifest.json#canonical_inventory",
    ):
        if marker not in policy:
            errors.append(f"memory-policy.md missing marker: {marker}")

    memory_readme = documents["README.md"]
    for name in REQUIRED_FILES[1:]:
        if f"`{name}`" not in memory_readme:
            errors.append(f"project-memory README missing reference: {name}")

    if not governance_readme.is_file():
        errors.append("governance/README.md is missing")
    else:
        governance_text = read_text(governance_readme)
        if "1. `project-memory/`" not in governance_text:
            errors.append("governance README does not put project-memory first")
        if "scripts/saee_project_memory_check.py" not in governance_text:
            errors.append("governance README missing project-memory validator")

    return errors


def counts(root: Path = ROOT) -> tuple[int, int, int, int, int, int]:
    memory_dir = root / "governance" / "project-memory"
    return (
        len(sections(read_text(memory_dir / "frozen-decisions.md"), "F")),
        len(sections(read_text(memory_dir / "active-questions.md"), "Q"))
        + len(sections(read_text(memory_dir / "active-questions.md"), "Q-V2")),
        len(sections(read_text(memory_dir / "rejected-options.md"), "R")),
        len(sections(read_text(memory_dir / "decision-log.md"), "D")),
        len(
            sections(
                read_text(memory_dir / "v2-transition-decisions.md"), "V2-F"
            )
        ),
        len(
            sections(
                read_text(memory_dir / "v2-transition-decisions.md"), "V2-P"
            )
        ),
    )


def main() -> int:
    errors = validate_project_memory(ROOT)
    if errors:
        print("SAEE_PROJECT_MEMORY_CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    frozen, active, rejected, decisions, v2_decisions, v2_principles = counts(ROOT)
    print(
        "SAEE_PROJECT_MEMORY_CHECK: PASS "
        f"files={len(REQUIRED_FILES)}/{len(REQUIRED_FILES)} "
        f"frozen={frozen} active={active} rejected={rejected} decisions={decisions} "
        f"v2_decisions={v2_decisions} v2_principles={v2_principles} "
        "capability_fact_source_unchanged=true production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
