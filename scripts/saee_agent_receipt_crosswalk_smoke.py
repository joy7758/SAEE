#!/usr/bin/env python3
"""Validate the local research-only SAEE agent receipt crosswalk."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "agent-interface/mappings/agent-receipt-crosswalk.v0.1.json"
DOC_PATHS = [
    ROOT / "docs/standards/SAEE_AGENT_RECEIPT_CROSSWALK.md",
    ROOT / "docs/standards/SAEE_AGENT_RECEIPT_GAP_ANALYSIS.md",
    ROOT / "docs/standards/SAEE_STANDARD_BOUNDARIES.md",
]

ROOT_KEYS = {
    "saee_agent_receipt_crosswalk_v0_1",
    "mapping_version",
    "scope",
    "source_basis",
    "claims",
    "truth_boundary",
}
SOURCE_KEYS = {
    "external_network_accessed",
    "normative_text_verified",
    "concept_labels_supplied_by_task",
    "external_concept_families",
    "notes",
}
CLAIM_KEYS = {
    "mapping_id",
    "external_concept",
    "purpose",
    "saee_concept",
    "saee_artifact_refs",
    "relationship",
    "implementation_status",
    "limitations",
}
RELATIONSHIPS = {"aligned", "partially_aligned", "different_scope", "missing_mapping"}
IMPLEMENTATION_STATUSES = {"existing", "planned", "not_implemented"}
EXTERNAL_CONCEPTS = {
    "agent_identity",
    "action_identity",
    "action_digest",
    "authorization_reference",
    "human_approval_evidence",
    "audit_trail",
    "evidence_composition",
    "verification_result",
    "accountability_claim",
}
CONCEPT_FAMILIES = {
    "agent_audit_trail_concepts",
    "signed_action_receipt_concepts",
    "human_authorization_evidence_concepts",
    "agent_accountability_composition_concepts",
}
TRUTH_BOUNDARY = {
    "ietf_compliance_claimed": False,
    "ietf_approval_claimed": False,
    "rfc_status_claimed": False,
    "rfc_compatibility_claimed": False,
    "external_standard_adopted": False,
    "regulatory_approval_claimed": False,
    "security_certification_claimed": False,
    "legal_evidence_status_claimed": False,
    "cryptographic_identity_verification_claimed": False,
    "production_ready": False,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_mapping(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or set(value) != ROOT_KEYS:
        return ["CROSSWALK_ROOT_INVALID"]
    if value.get("saee_agent_receipt_crosswalk_v0_1") is not True:
        errors.append("CROSSWALK_MARKER_INVALID")
    if value.get("mapping_version") != "0.1.0":
        errors.append("CROSSWALK_VERSION_INVALID")
    if value.get("scope") != "semantic_analysis_only":
        errors.append("CROSSWALK_SCOPE_INVALID")

    source = value.get("source_basis")
    if not isinstance(source, dict) or set(source) != SOURCE_KEYS:
        errors.append("CROSSWALK_SOURCE_BASIS_INVALID")
    elif (
        source.get("external_network_accessed") is not False
        or source.get("normative_text_verified") is not False
        or source.get("concept_labels_supplied_by_task") is not True
        or set(source.get("external_concept_families", [])) != CONCEPT_FAMILIES
        or not isinstance(source.get("notes"), str)
        or not source["notes"]
    ):
        errors.append("CROSSWALK_SOURCE_BOUNDARY_INVALID")

    claims = value.get("claims")
    if not isinstance(claims, list) or len(claims) != 9:
        errors.append("CROSSWALK_CLAIM_COUNT_INVALID")
    else:
        mapping_ids: set[str] = set()
        concepts: set[str] = set()
        for index, claim in enumerate(claims):
            prefix = f"CROSSWALK_CLAIM_{index}"
            if not isinstance(claim, dict):
                errors.append(f"{prefix}_FIELDS_INVALID")
                continue
            concept = claim.get("external_concept")
            concept_seen = concept in concepts
            if concept in EXTERNAL_CONCEPTS and not concept_seen:
                concepts.add(concept)
            if set(claim) != CLAIM_KEYS:
                errors.append(f"{prefix}_FIELDS_INVALID")
                continue
            mapping_id = claim.get("mapping_id")
            if not isinstance(mapping_id, str) or not mapping_id or mapping_id in mapping_ids:
                errors.append(f"{prefix}_MAPPING_ID_INVALID")
            else:
                mapping_ids.add(mapping_id)
            if concept not in EXTERNAL_CONCEPTS or concept_seen:
                errors.append(f"{prefix}_EXTERNAL_CONCEPT_INVALID")
            if claim.get("relationship") not in RELATIONSHIPS:
                errors.append(f"{prefix}_RELATIONSHIP_INVALID")
            if claim.get("implementation_status") not in IMPLEMENTATION_STATUSES:
                errors.append(f"{prefix}_IMPLEMENTATION_STATUS_INVALID")
            for text_key in ("purpose", "saee_concept"):
                if not isinstance(claim.get(text_key), str) or not claim[text_key]:
                    errors.append(f"{prefix}_{text_key.upper()}_INVALID")
            refs = claim.get("saee_artifact_refs")
            if not isinstance(refs, list) or not refs or not all(
                isinstance(ref, str) and ref and (ROOT / ref).is_file() for ref in refs
            ):
                errors.append(f"{prefix}_ARTIFACT_REFS_INVALID")
            limitations = claim.get("limitations")
            if not isinstance(limitations, list) or not limitations or not all(
                isinstance(item, str) and item for item in limitations
            ):
                errors.append(f"{prefix}_LIMITATIONS_INVALID")
        if concepts != EXTERNAL_CONCEPTS:
            errors.append("CROSSWALK_REQUIRED_CONCEPTS_MISSING")

    if value.get("truth_boundary") != TRUTH_BOUNDARY:
        errors.append("CROSSWALK_TRUTH_BOUNDARY_INVALID")
    return errors


def main() -> None:
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    require(validate_mapping(mapping) == [], "valid mapping rejected")

    invalid_relationship = copy.deepcopy(mapping)
    invalid_relationship["claims"][0]["relationship"] = "compliant"
    require(
        validate_mapping(invalid_relationship) == ["CROSSWALK_CLAIM_0_RELATIONSHIP_INVALID"],
        "invalid relationship reason",
    )
    missing_limitations = copy.deepcopy(mapping)
    del missing_limitations["claims"][1]["limitations"]
    require(
        validate_mapping(missing_limitations) == ["CROSSWALK_CLAIM_1_FIELDS_INVALID"],
        "missing limitations reason",
    )

    canonical = json.dumps(mapping, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(10):
        repeated = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
        require(validate_mapping(repeated) == [], "deterministic validation")
        require(
            json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "deterministic canonical form",
        )

    for path in DOC_PATHS:
        text = path.read_text(encoding="utf-8")
        require("不" in text or "not" in text.lower(), f"boundary language required: {path.name}")
        require("production_ready" in text or "生产就绪" in text, f"production boundary required: {path.name}")
    crosswalk_doc = DOC_PATHS[0].read_text(encoding="utf-8")
    require("Compatible ≠ Compliant" in crosswalk_doc, "compatibility principle")
    require("Mapping ≠ Standard Adoption" in crosswalk_doc, "mapping principle")
    require("Analysis ≠ Certification" in crosswalk_doc, "analysis principle")
    gap_doc = DOC_PATHS[1].read_text(encoding="utf-8")
    require("External receipts describe actions" in gap_doc, "external receipt principle")
    require("SAEE evaluates evidence sufficiency" in gap_doc, "SAEE adequacy principle")

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    require(not imported_roots.intersection({"subprocess", "socket", "requests", "httpx", "urllib"}), "external capability import")

    print("SAEE_AGENT_RECEIPT_CROSSWALK_SMOKE: PASS")
    print("valid_mapping_cases=1/1")
    print("invalid_mapping_cases=2/2")
    print("mapping_rows=9/9")
    print("documentation_boundary_cases=3/3")
    print("deterministic_runs=10/10")
    print("unsupported_claims=0")
    print("external_network_accessed=false")
    print("normative_text_verified=false")
    print("ietf_compliance_claimed=false")
    print("rfc_compatibility_claimed=false")
    print("standard_adopted=false")
    print("subprocess_started=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
