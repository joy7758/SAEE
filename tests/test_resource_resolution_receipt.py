import unittest
import base64
import hashlib
from typing import Any

from saee_backend.services.resource_resolution_receipt import (
    validate_resource_resolution_receipt,
    RESOURCE_DIGEST_INVALID,
    compute_receipt_digest,
)

def _create_valid_receipt() -> dict[str, Any]:
    raw_content = b"hello world"
    encoded_content = base64.b64encode(raw_content).decode("ascii")
    content_digest = hashlib.sha256(raw_content).hexdigest()

    receipt = {
        "saee_resource_resolution_receipt_v0_1": True,
        "schema_version": "0.1.0",
        "receipt_id": "saee-resource-resolution-0123456789abcdef",
        "receipt_type": "external_resource_resolution",
        "created_at": "2024-01-01T00:00:00Z",
        "agent_id": "agent_123",
        "requested_resource": "test_resource",
        "requested_resource_type": "software_package",
        "resolved_uri": "https://example.com/resource",
        "registry_or_host": "example.com",
        "publisher_identity": {
            "identity_claim": "test_publisher",
            "claim_status": "declared_not_independently_verified"
        },
        "publisher_verification_method": "registry_namespace_record",
        "content_binding": {
            "mode": "synthetic_inline_bytes",
            "encoding": "base64",
            "inline_base64": encoded_content,
            "byte_length": len(raw_content)
        },
        "content_digest": content_digest,
        "digest_algorithm": "sha-256",
        "retrieval_timestamp": "2024-01-01T00:00:00Z",
        "policy_decision_ref": "policy_123",
        "authorization_boundary": {
            "allowed_action": "inspect_metadata_and_hash_only",
            "install": False,
            "import": False,
            "execute": False,
            "network": False,
            "permission_expansion": False
        },
        "sandbox_ref": "sandbox_123",
        "sandbox_boundary": {
            "kind": "offline_non_execution_boundary",
            "network": False,
            "subprocess": False,
            "execution": False
        },
        "external_effect": {
            "status": "not_executed",
            "side_effect": "no_side_effect",
            "execution_effect_observed": False
        },
        "truth_boundary": {
            "uri_dereferenced": False,
            "publisher_identity_verified": False,
            "external_resource_authenticity_verified": False,
            "license_verified": False,
            "malware_scanned": False,
            "supply_chain_verified": False,
            "install_performed": False,
            "resource_imported": False,
            "candidate_code_executed": False,
            "production_ready": False
        }
    }
    receipt["integrity"] = {
        "canonicalization": "saee-canonical-json-v0.1",
        "digest_algorithm": "sha-256",
        "digest_scope": "all_receipt_fields_except_integrity",
        "receipt_digest": compute_receipt_digest(receipt)
    }
    return receipt

class ResourceResolutionReceiptTest(unittest.TestCase):
    def test_valid_receipt(self):
        receipt = _create_valid_receipt()
        result = validate_resource_resolution_receipt(receipt)
        self.assertTrue(result["valid"], result.get("reason_codes"))

    def test_invalid_base64_decoding_fails(self):
        receipt = _create_valid_receipt()

        # Valid schema pattern: ^[A-Za-z0-9+/]+={0,2}$ and minimum length 4
        # Invalid base64 that causes error: 'abcde' raises binascii.Error (subclass of ValueError)
        # because its length is 1 more than a multiple of 4.
        receipt["content_binding"]["inline_base64"] = "abcde"
        receipt["integrity"]["receipt_digest"] = compute_receipt_digest(receipt)

        result = validate_resource_resolution_receipt(receipt)
        self.assertFalse(result["valid"])
        self.assertIn(RESOURCE_DIGEST_INVALID, result["reason_codes"])

if __name__ == '__main__':
    unittest.main()
