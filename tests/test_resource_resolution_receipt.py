import copy
import unittest

from saee_backend.services.resource_resolution_receipt import (
    RESOURCE_DIGEST_INVALID,
    compute_receipt_digest,
    validate_resource_resolution_receipt,
)


class TestResourceResolutionReceipt(unittest.TestCase):
    def setUp(self):
        self.valid_receipt = {
            "saee_resource_resolution_receipt_v0_1": True,
            "schema_version": "0.1.0",
            "receipt_id": "saee-resource-resolution-0123456789abcdef",
            "receipt_type": "external_resource_resolution",
            "created_at": "2024-01-01T00:00:00Z",
            "agent_id": "test_agent",
            "requested_resource": "test",
            "requested_resource_type": "artifact",
            "resolved_uri": "https://example.com/test",
            "registry_or_host": "example.com",
            "publisher_identity": {
                "identity_claim": "test_publisher",
                "claim_status": "declared_not_independently_verified"
            },
            "publisher_verification_method": "domain_control_declared",
            "content_binding": {
                "mode": "synthetic_inline_bytes",
                "encoding": "base64",
                "inline_base64": "dGVzdA==",
                "byte_length": 4
            },
            "content_digest": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
            "digest_algorithm": "sha-256",
            "retrieval_timestamp": "2024-01-01T00:00:00Z",
            "policy_decision_ref": "test_policy",
            "authorization_boundary": {
                "allowed_action": "inspect_metadata_and_hash_only",
                "install": False,
                "import": False,
                "execute": False,
                "network": False,
                "permission_expansion": False
            },
            "sandbox_ref": "test_sandbox",
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
            },
            "integrity": {
                "canonicalization": "saee-canonical-json-v0.1",
                "digest_algorithm": "sha-256",
                "digest_scope": "all_receipt_fields_except_integrity",
                "receipt_digest": "will_be_recomputed"
            }
        }
        self.valid_receipt["integrity"]["receipt_digest"] = compute_receipt_digest(self.valid_receipt)

    def test_valid_receipt(self):
        result = validate_resource_resolution_receipt(self.valid_receipt)
        self.assertTrue(result["valid"])

    def test_invalid_base64_decoding_error(self):
        invalid_receipt = copy.deepcopy(self.valid_receipt)
        # Use an invalid base64 string that passes schema validation
        # The schema requires inline_base64 to match ^[A-Za-z0-9+/]+={0,2}$ and length 4-4096
        # 'abcde=' matches the schema, but is invalid base64 (length 6 not a multiple of 4, or rather 5 data chars).
        invalid_receipt["content_binding"]["inline_base64"] = "abcde="
        result = validate_resource_resolution_receipt(invalid_receipt)
        self.assertFalse(result["valid"])
        self.assertIn(RESOURCE_DIGEST_INVALID, result["reason_codes"])

if __name__ == "__main__":
    unittest.main()
