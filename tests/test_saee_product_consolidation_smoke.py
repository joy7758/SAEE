import unittest
import copy
from scripts.saee_product_consolidation_smoke import validate, SECTIONS


def get_valid_value() -> dict:
    return {
        "canonical_identity": {
            "theory_name": "Silicon-Amplified Evolutionary Ecology",
            "engineering_core": "Digital Biosphere Evolution Engine",
            "product_surface": "Agent Reliability Evaluation Capability Layer",
            "primary_language": "zh-CN",
        },
        "modules": [{"module_id": f"mod_{i}", "source": f"src_{i}"} for i in range(10)],
        "truth_boundary": {"a": False, "b": False},
    }

def get_valid_readme() -> str:
    sections = "\n".join(SECTIONS)
    return f"# SAEE 智能体可靠性评估基础设施\n\n{sections}\n\nSome content."


class TestSaeeProductConsolidationSmoke(unittest.TestCase):
    def test_valid_happy_path(self) -> None:
        value = get_valid_value()
        readme = get_valid_readme()
        errors = validate(value, readme)
        self.assertEqual(errors, [])

    def test_map_not_object(self) -> None:
        readme = get_valid_readme()
        self.assertEqual(validate("not_a_dict", readme), ["MAP_NOT_OBJECT"])
        self.assertEqual(validate([], readme), ["MAP_NOT_OBJECT"])

    def test_theory_identity_drift(self) -> None:
        value = get_valid_value()
        value["canonical_identity"]["theory_name"] = "Wrong Theory"
        readme = get_valid_readme()
        self.assertIn("THEORY_IDENTITY_DRIFT", validate(value, readme))

    def test_engineering_core_drift(self) -> None:
        value = get_valid_value()
        value["canonical_identity"]["engineering_core"] = "Wrong Core"
        readme = get_valid_readme()
        self.assertIn("ENGINEERING_CORE_DRIFT", validate(value, readme))

    def test_product_surface_drift(self) -> None:
        value = get_valid_value()
        value["canonical_identity"]["product_surface"] = "Wrong Surface"
        readme = get_valid_readme()
        self.assertIn("PRODUCT_SURFACE_DRIFT", validate(value, readme))

    def test_primary_language_invalid(self) -> None:
        value = get_valid_value()
        value["canonical_identity"]["primary_language"] = "en-US"
        readme = get_valid_readme()
        self.assertIn("PRIMARY_LANGUAGE_INVALID", validate(value, readme))

    def test_module_count_insufficient(self) -> None:
        value = get_valid_value()
        value["modules"] = value["modules"][:9]
        readme = get_valid_readme()
        self.assertIn("MODULE_COUNT_INSUFFICIENT", validate(value, readme))

    def test_module_id_duplicate(self) -> None:
        value = get_valid_value()
        value["modules"][1]["module_id"] = value["modules"][0]["module_id"]
        readme = get_valid_readme()
        self.assertIn("MODULE_ID_DUPLICATE", validate(value, readme))

    def test_local_path_exposed(self) -> None:
        value = get_valid_value()
        value["modules"][0]["source"] = "/Users/somebody/local"
        readme = get_valid_readme()
        self.assertIn("LOCAL_PATH_EXPOSED", validate(value, readme))

        value["modules"][0]["source"] = "/home/somebody/local"
        self.assertIn("LOCAL_PATH_EXPOSED", validate(value, readme))

    def test_audit_first_drift(self) -> None:
        for bad_id in {"audit_evidence", "evidence_engine_reference", "mcp_interface"}:
            value = get_valid_value()
            value["modules"].append({"module_id": bad_id, "core": True})
            readme = get_valid_readme()
            self.assertIn("AUDIT_FIRST_DRIFT", validate(value, readme))

    def test_truth_boundary_invalid(self) -> None:
        value = get_valid_value()
        value["truth_boundary"] = {}
        readme = get_valid_readme()
        self.assertIn("TRUTH_BOUNDARY_INVALID", validate(value, readme))

        value = get_valid_value()
        value["truth_boundary"]["some_key"] = True
        self.assertIn("TRUTH_BOUNDARY_INVALID", validate(value, readme))

    def test_readme_section_missing(self) -> None:
        value = get_valid_value()
        readme = get_valid_readme().replace("为什么需要 SAEE", "Missing Section")
        self.assertIn("README_SECTION_MISSING", validate(value, readme))

    def test_readme_chinese_first_invalid(self) -> None:
        value = get_valid_value()
        readme = "Something else\n" + get_valid_readme()
        self.assertIn("README_CHINESE_FIRST_INVALID", validate(value, readme))

    def test_canonical_rename_forbidden(self) -> None:
        value = get_valid_value()
        readme = get_valid_readme() + "\nSmart Agent Execution & Evidence"
        self.assertIn("CANONICAL_RENAME_FORBIDDEN", validate(value, readme))


if __name__ == "__main__":
    unittest.main()
