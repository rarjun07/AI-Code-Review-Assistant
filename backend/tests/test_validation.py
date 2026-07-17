import unittest
from types import SimpleNamespace

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.user import PasswordReset, UserCreate, UserUpdate
from app.services.documentation_service import generate_documentation
from app.services.report_export_service import (
    build_report_html,
    build_report_markdown,
)
from app.utils.validation import sanitize_filename, validate_python_upload


class UploadValidationTests(unittest.TestCase):
    def test_sanitize_filename_removes_path(self):
        self.assertEqual(sanitize_filename("../example.py"), "example.py")

    def test_validate_python_upload_accepts_python_file(self):
        filename = validate_python_upload("example.py", b"print('ok')\n")

        self.assertEqual(filename, "example.py")

    def test_validate_python_upload_rejects_non_python_file(self):
        with self.assertRaises(HTTPException) as context:
            validate_python_upload("example.txt", b"hello")

        self.assertEqual(context.exception.status_code, 400)

    def test_validate_python_upload_rejects_empty_file(self):
        with self.assertRaises(HTTPException) as context:
            validate_python_upload("example.py", b"")

        self.assertEqual(context.exception.status_code, 400)


class UserValidationTests(unittest.TestCase):
    def test_user_create_accepts_valid_payload(self):
        user = UserCreate(
            name="Arjun",
            email="arjun@example.com",
            password="Password123",
        )

        self.assertEqual(user.name, "Arjun")

    def test_user_create_rejects_weak_password(self):
        with self.assertRaises(ValidationError):
            UserCreate(
                name="Arjun",
                email="arjun@example.com",
                password="password",
            )

    def test_user_update_trims_name(self):
        user = UserUpdate(
            name=" Arjun ",
            email="arjun@example.com",
        )

        self.assertEqual(user.name, "Arjun")

    def test_password_reset_rejects_weak_password(self):
        with self.assertRaises(ValidationError):
            PasswordReset(
                email="arjun@example.com",
                new_password="password",
            )


class DocumentationMetricsTests(unittest.TestCase):
    def test_generate_documentation_includes_code_metrics(self):
        documentation = generate_documentation(
            "\n".join(
                [
                    "class Example:",
                    "    def method(self):",
                    "        return True",
                    "",
                    "def helper():",
                    "    return False",
                ]
            ),
            "example.py",
        )

        self.assertEqual(documentation["metrics"]["number_of_classes"], 1)
        self.assertEqual(documentation["metrics"]["number_of_functions"], 2)
        self.assertEqual(documentation["metrics"]["total_lines_of_code"], 6)
        self.assertGreater(
            documentation["metrics"]["average_function_length"],
            0,
        )


class ReportExportTests(unittest.TestCase):
    def test_report_export_generates_markdown_and_html(self):
        report = SimpleNamespace(
            id=7,
            filename="example.py",
            created_at="2026-07-11",
            pylint_report={"score": "9.5", "issues": []},
            bandit_report={"total_issues": 0, "issues": []},
            radon_report={
                "grades": ["A"],
                "complexity": "example.py\n",
                "maintainability": "example.py - A\n",
            },
            ai_review={
                "overall_rating": "Good",
                "summary": "Clean code.",
                "bugs": [],
                "security_recommendations": [],
                "optimization_suggestions": [],
                "naming_suggestions": [],
                "refactoring_suggestions": [],
                "performance_recommendations": [],
                "best_practices": [],
            },
            documentation_report={
                "markdown": "# Documentation for example.py"
            },
        )

        markdown = build_report_markdown(report)
        html = build_report_html(report)

        self.assertIn("AI Code Review Report", markdown)
        self.assertIn("Pylint Score: 9.5/10", markdown)
        self.assertIn("<!doctype html>", html)


if __name__ == "__main__":
    unittest.main()
