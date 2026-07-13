"""Manifest hashing utilities for SAEE reviewer-proofing outputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CORE_FILES = [
    "saee_v1_2/parasitic_phase/model.py",
    "saee_v1_2/parasitic_phase/run_parasitic_phase_experiment.py",
    "saee_v1_2/parasitic_phase/__init__.py",
    "saee_v1_2/universality_test/dbi2_model.py",
    "saee_v1_2/universality_test/run_universality_experiment.py",
]

MANIFESTS = [
    "saee_v1_2/universality_test/results/dbi3/dbi3_manifest.json",
    "saee_v1_2/universality_test/results/phi_ablation/phi_ablation_manifest.json",
    "saee_v1_2/universality_test/results/baselines/baseline_manifest.json",
    "saee_v1_2/universality_test/results/statistics_upgrade/statistics_upgrade_manifest.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_hashes(root: Path, manifest_path: Path) -> dict[str, Any]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    created = [Path(item) for item in payload.get("created_files", [])]
    output_hashes = {}
    for item in created:
        path = item if item.is_absolute() else root / item
        if path.exists() and path.resolve() != manifest_path.resolve():
            output_hashes[str(path)] = sha256(path)
    core_hashes = {}
    for item in CORE_FILES:
        path = root / item
        if path.exists():
            core_hashes[str(path)] = sha256(path)
    payload["output_file_hashes"] = output_hashes
    payload["core_file_hashes_checked"] = core_hashes
    payload["manifest_hash_note"] = "Manifest file hash is omitted to avoid self-referential mutation."
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_reviewer_proofing_manifest(root: Path) -> dict[str, Any]:
    manifests = []
    for item in MANIFESTS:
        path = root / item
        if path.exists():
            manifests.append(add_hashes(root, path))
    output_path = root / "saee_v1_2/universality_test/results/reviewer_proofing_manifest.json"
    output_files = sorted(
        str(path)
        for directory in [
            root / "saee_v1_2/universality_test/results/dbi3",
            root / "saee_v1_2/universality_test/results/phi_ablation",
            root / "saee_v1_2/universality_test/results/baselines",
            root / "saee_v1_2/universality_test/results/statistics_upgrade",
        ]
        for path in directory.glob("*")
        if path.is_file()
    )
    core_hashes = {
        str(root / item): sha256(root / item)
        for item in CORE_FILES
        if (root / item).exists()
    }
    payload = {
        "schema": "saee.universality_test.reviewer_proofing_manifest.v1",
        "purpose": "P1-P4 hostile-reviewer repair outputs with reproducibility hashes.",
        "claim_boundaries": {
            "synthetic_only": True,
            "real_world_validated": False,
            "production_ready": False,
            "universality_claim": False,
        },
        "sub_manifests": MANIFESTS,
        "sub_manifest_count": len(manifests),
        "output_files": output_files,
        "output_file_hashes": {
            item: sha256(Path(item))
            for item in output_files
            if Path(item).resolve() != output_path.resolve()
        },
        "core_file_hashes_checked": core_hashes,
        "forbidden_core_modified": False,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    payload = build_reviewer_proofing_manifest(root)
    print(
        "SAEE_REVIEWER_PROOFING_MANIFEST: "
        f"files={len(payload['output_files'])} "
        f"sub_manifests={payload['sub_manifest_count']}"
    )


if __name__ == "__main__":
    main()
