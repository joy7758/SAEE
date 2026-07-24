import unittest

from saee_backend.services.resource_resolution_receipt import (
    validate_resource_resolution_json,
    RESOURCE_SCHEMA_INVALID,
)

class ResourceResolutionReceiptTest(unittest.TestCase):
    def test_validate_resource_resolution_json_malformed(self):
        result = validate_resource_resolution_json("{")
        self.assertFalse(result["valid"])
        self.assertIn(RESOURCE_SCHEMA_INVALID, result["reason_codes"])

    def test_validate_resource_resolution_json_duplicate_keys(self):
        result = validate_resource_resolution_json('{"key": "value", "key": "value2"}')
        self.assertFalse(result["valid"])
        self.assertIn(RESOURCE_SCHEMA_INVALID, result["reason_codes"])

if __name__ == "__main__":
    unittest.main()
