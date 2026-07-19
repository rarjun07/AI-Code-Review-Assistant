import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.services.pylint_service import run_pylint


class PylintServiceTests(unittest.TestCase):
    @patch("app.services.pylint_service.subprocess.run")
    def test_uses_original_filename_instead_of_storage_name(self, run):
        run.side_effect = [
            SimpleNamespace(stdout=json.dumps([])),
            SimpleNamespace(stdout="Your code has been rated at 10.00/10"),
        ]

        with tempfile.TemporaryDirectory() as directory:
            stored_file = Path(directory) / "uuid_main.py"
            stored_file.write_text("print('hello')\n", encoding="utf-8")

            report = run_pylint(str(stored_file), "main.py")

        self.assertEqual(report["score"], "10.00")
        self.assertEqual(run.call_count, 2)

        for call in run.call_args_list:
            command = call.args[0]
            self.assertIn("--from-stdin", command)
            self.assertIn("main.py", command)
            self.assertNotIn(str(stored_file), command)
            self.assertEqual(call.kwargs["input"], "print('hello')\n")


if __name__ == "__main__":
    unittest.main()
