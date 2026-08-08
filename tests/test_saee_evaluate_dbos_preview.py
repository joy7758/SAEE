import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from scripts.saee_evaluate_dbos_preview import _load, main


def get_valid_envelope() -> dict:
    executions = []
    evidence = []
    for index, role in enumerate(("research", "analysis", "review"), start=1):
        execution_id = f"execution:{index}:{role}"
        executions.append(
            {
                "execution_id": execution_id,
                "entity_reference": {"reference_id": f"entity:{role}"},
                "status": "CREATED",
            }
        )
        evidence.append(
            {
                "evidence_id": f"evidence:{index}:{role}",
                "execution_reference": {"reference_id": execution_id},
                "integrity_status": "PENDING",
            }
        )
    return {
        "contract_version": "dba.dbos-saee-developer-preview/v0.1",
        "source_demo_id": "DBOS-MULTI-AGENT-TRUST-DEMO-V0.1",
        "execution_history": executions,
        "evidence_references": evidence,
        "validation_results": [{"result": "PASS"} for _ in range(9)],
        "resource_information": {
            "model_call_count": 0,
            "network_call_count": 0,
            "tool_call_count": 0,
            "external_side_effect_count": 0,
        },
    }


class TestSaeeEvaluateDbosPreview(unittest.TestCase):
    def test_load_prevents_path_traversal(self) -> None:
        """Test that _load raises a PermissionError for paths outside the current directory."""
        with self.assertRaises(PermissionError):
            _load("../../etc/passwd")

    def test_load_allows_valid_path(self) -> None:
        """Test that _load works for paths inside the current directory."""
        cwd = Path.cwd()
        # Create a temporary file in the current working directory
        with NamedTemporaryFile(dir=cwd, suffix=".json", delete=False) as f:
            f.write(b'{"key": "value"}')
            temp_path = f.name

        try:
            result = _load(temp_path)
            self.assertEqual(result, {"key": "value"})
        finally:
            os.remove(temp_path)

    def test_main_stdin_valid(self) -> None:
        valid_envelope = get_valid_envelope()
        stdin_content = json.dumps(valid_envelope)
        with patch("sys.argv", ["saee_evaluate_dbos_preview.py"]):
            with patch("sys.stdin", StringIO(stdin_content)):
                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    result = main()
                    self.assertEqual(result, 0)
                    output = json.loads(mock_stdout.getvalue())
                    self.assertIn("reliability_assessment", output)
                    self.assertEqual(output["reliability_assessment"]["status"], "NOT_ASSESSED")

    def test_main_stdin_valid_with_envelope_wrapper(self) -> None:
        valid_envelope = get_valid_envelope()
        stdin_content = json.dumps({"dbos_to_saee_envelope": valid_envelope})
        with patch("sys.argv", ["saee_evaluate_dbos_preview.py"]):
            with patch("sys.stdin", StringIO(stdin_content)):
                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    result = main()
                    self.assertEqual(result, 0)
                    output = json.loads(mock_stdout.getvalue())
                    self.assertIn("reliability_assessment", output)
                    self.assertEqual(output["reliability_assessment"]["status"], "NOT_ASSESSED")

    def test_main_file_valid(self) -> None:
        valid_envelope = get_valid_envelope()
        # Write inside the current working directory: _load rejects paths outside cwd.
        with NamedTemporaryFile(mode="w", dir=Path.cwd(), suffix=".json", delete=False) as f:
            json.dump(valid_envelope, f)
            filepath = f.name

        try:
            with patch("sys.argv", ["saee_evaluate_dbos_preview.py", "--input", filepath]):
                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    result = main()
                    self.assertEqual(result, 0)
                    output = json.loads(mock_stdout.getvalue())
                    self.assertIn("reliability_assessment", output)
                    self.assertEqual(output["reliability_assessment"]["status"], "NOT_ASSESSED")
        finally:
            os.remove(filepath)

    def test_main_invalid_json(self) -> None:
        invalid_json_content = "{ invalid_json: "
        with patch("sys.argv", ["saee_evaluate_dbos_preview.py"]):
            with patch("sys.stdin", StringIO(invalid_json_content)):
                with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                    result = main()
                    self.assertEqual(result, 2)
                    error_output = json.loads(mock_stderr.getvalue())
                    self.assertEqual(error_output["error"], "DBOS_PREVIEW_INPUT_READ_FAILED")

    def test_main_dbos_input_error(self) -> None:
        invalid_envelope = get_valid_envelope()
        invalid_envelope["contract_version"] = "invalid_version"
        stdin_content = json.dumps(invalid_envelope)
        with patch("sys.argv", ["saee_evaluate_dbos_preview.py"]):
            with patch("sys.stdin", StringIO(stdin_content)):
                with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                    result = main()
                    self.assertEqual(result, 2)
                    error_output = json.loads(mock_stderr.getvalue())
                    self.assertEqual(error_output["error"], "DBOS_PREVIEW_CONTRACT_UNSUPPORTED")

    def test_main_file_not_found(self) -> None:
        with patch("sys.argv", ["saee_evaluate_dbos_preview.py", "--input", "nonexistent_file.json"]):
            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                result = main()
                self.assertEqual(result, 2)
                error_output = json.loads(mock_stderr.getvalue())
                self.assertEqual(error_output["error"], "DBOS_PREVIEW_INPUT_READ_FAILED")


if __name__ == "__main__":
    unittest.main()
