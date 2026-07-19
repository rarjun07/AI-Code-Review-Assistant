import json
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.bandit_service import run_bandit
from app.services.radon_service import run_radon


class StaticAnalysisServiceTests(unittest.TestCase):
    @patch("app.services.bandit_service.subprocess.run")
    def test_bandit_uses_current_python_environment(self, run):
        run.return_value = SimpleNamespace(
            stdout=json.dumps({"results": [], "metrics": {}})
        )

        report = run_bandit("example.py")

        self.assertEqual(report["total_issues"], 0)
        command = run.call_args.args[0]
        self.assertEqual(command[:3], [sys.executable, "-m", "bandit"])

    @patch("app.services.radon_service.subprocess.run")
    def test_radon_uses_current_python_environment(self, run):
        run.side_effect = [
            SimpleNamespace(stdout="example.py\n    F 1:0 helper - A (1)\n"),
            SimpleNamespace(stdout="example.py - A\n"),
        ]

        report = run_radon("example.py")

        self.assertEqual(report["grades"], ["1"])
        for call in run.call_args_list:
            self.assertEqual(call.args[0][:3], [sys.executable, "-m", "radon"])


if __name__ == "__main__":
    unittest.main()
