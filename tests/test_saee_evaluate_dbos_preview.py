import os
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from scripts.saee_evaluate_dbos_preview import _load


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
