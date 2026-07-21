"""Tests for bounded clean-room event-chain and Merkle integrity traits."""

from __future__ import annotations

import copy
import hashlib
import unittest

from saee_backend.services.agent_evidence_integrity import (
    IntegritySubsetError,
    build_event_chain,
    canonical_jcs_safe_subset,
    event_digest,
    merkle_root,
    verify_event_chain,
    verify_ed25519_signature,
    verify_merkle_root,
)


EVENTS = [
    {"event_index": 0, "event_id": "event:001", "action": "inspect", "payload_digest": "sha256:" + "a" * 64},
    {"event_index": 1, "event_id": "event:002", "action": "report", "payload_digest": "sha256:" + "b" * 64},
    {"event_index": 2, "event_id": "event:003", "action": "stop", "payload_digest": "sha256:" + "c" * 64},
]

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAuAuE0oyj4NIuxyj2eRTa2pNLr+xpKapzlrXy2GE+rGM=
-----END PUBLIC KEY-----
"""
SIGNED_ROOT = b"sha256:bec1ec4035c01f77da9b77a5c839cd497b9dc66adc08a571ad26e39e4465651b"
SIGNATURE = "3IeivmeZ8HvTt7RGzVVoPrcAJ+LQuppadL6tLKZ6Xbq9IfbuFBkmglBochqU5WYuqUpjnZSSzdsMVtmdOpCcDg=="


class AgentEvidenceIntegrityTest(unittest.TestCase):
    def test_01_canonical_subset_is_deterministic(self) -> None:
        left = {"z": 1, "a": [True, None, "x"]}
        right = {"a": [True, None, "x"], "z": 1}
        self.assertEqual(canonical_jcs_safe_subset(left), b'{"a":[true,null,"x"],"z":1}')
        self.assertEqual(canonical_jcs_safe_subset(left), canonical_jcs_safe_subset(right))

    def test_02_floats_are_rejected(self) -> None:
        with self.assertRaises(IntegritySubsetError):
            canonical_jcs_safe_subset({"value": 1.5})

    def test_03_non_ascii_is_rejected(self) -> None:
        with self.assertRaises(IntegritySubsetError):
            canonical_jcs_safe_subset({"value": "非ASCII"})

    def test_04_unsafe_integer_is_rejected(self) -> None:
        with self.assertRaises(IntegritySubsetError):
            canonical_jcs_safe_subset({"value": 9_007_199_254_740_992})

    def test_05_event_digest_is_sha256_of_canonical_subset(self) -> None:
        expected = "sha256:" + hashlib.sha256(canonical_jcs_safe_subset(EVENTS[0])).hexdigest()
        self.assertEqual(event_digest(EVENTS[0]), expected)

    def test_06_chain_verifies_and_binds_previous_entry(self) -> None:
        chain = build_event_chain(EVENTS)
        self.assertTrue(verify_event_chain(EVENTS, chain))
        self.assertIsNone(chain[0]["previous_chain_digest"])
        self.assertEqual(chain[1]["previous_chain_digest"], chain[0]["chain_digest"])

    def test_07_chain_rejects_event_tamper(self) -> None:
        chain = build_event_chain(EVENTS)
        tampered = copy.deepcopy(EVENTS)
        tampered[1]["action"] = "tampered"
        self.assertFalse(verify_event_chain(tampered, chain))

    def test_08_chain_rejects_reordering(self) -> None:
        chain = build_event_chain(EVENTS)
        reordered = [EVENTS[1], EVENTS[0], EVENTS[2]]
        self.assertFalse(verify_event_chain(reordered, chain))

    def test_09_merkle_root_verifies_with_odd_leaf_duplication(self) -> None:
        digests = [event_digest(event) for event in EVENTS]
        root = merkle_root(digests)
        self.assertTrue(root.startswith("sha256:"))
        self.assertTrue(verify_merkle_root(digests, root))

    def test_10_merkle_root_rejects_tamper(self) -> None:
        digests = [event_digest(event) for event in EVENTS]
        root = merkle_root(digests)
        tampered = list(digests)
        tampered[0] = "sha256:" + "0" * 64
        self.assertFalse(verify_merkle_root(tampered, root))

    def test_11_empty_chain_and_merkle_are_rejected(self) -> None:
        with self.assertRaises(IntegritySubsetError):
            build_event_chain([])
        with self.assertRaises(IntegritySubsetError):
            merkle_root([])

    def test_12_integrity_functions_do_not_mutate_events(self) -> None:
        events = copy.deepcopy(EVENTS)
        original = copy.deepcopy(events)
        build_event_chain(events)
        self.assertEqual(events, original)

    def test_13_ed25519_signature_verifies_with_existing_openssl(self) -> None:
        result = verify_ed25519_signature(SIGNED_ROOT, PUBLIC_KEY, SIGNATURE)
        self.assertEqual(result["check"], "PASS")
        self.assertEqual(result["reason"], "verified_by_system_openssl")
        self.assertTrue(result["local_crypto_subprocess_started"])
        self.assertTrue(result["openssl_version"].startswith("OpenSSL 3."))

    def test_14_ed25519_signature_tamper_fails(self) -> None:
        result = verify_ed25519_signature(
            SIGNED_ROOT + b"0", PUBLIC_KEY, SIGNATURE
        )
        self.assertEqual(result["check"], "FAIL")
        self.assertEqual(result["reason"], "signature_verification_failed")

    def test_15_ed25519_missing_openssl_is_not_run(self) -> None:
        result = verify_ed25519_signature(
            SIGNED_ROOT, PUBLIC_KEY, SIGNATURE, openssl_path="/missing/openssl"
        )
        self.assertEqual(result["check"], "NOT_RUN")
        self.assertEqual(result["reason"], "openssl_unavailable")
        self.assertFalse(result["local_crypto_subprocess_started"])


if __name__ == "__main__":
    unittest.main()
