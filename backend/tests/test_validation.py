import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from jose import jwt
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.routes.auth import router as auth_router
from app.schemas.user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    UserCreate,
    UserUpdate,
)
from app.services.documentation_service import generate_documentation
from app.services.report_export_service import (
    build_report_html,
    build_report_markdown,
)
from app.utils.security import (
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    reset_token_matches_password,
    verify_password,
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

    def test_validate_python_upload_rejects_oversized_file(self):
        with self.assertRaises(HTTPException) as context:
            validate_python_upload("large.py", b"x" * (1024 * 1024 + 1))

        self.assertEqual(context.exception.status_code, 413)


class UserValidationTests(unittest.TestCase):
    def test_user_create_accepts_valid_payload(self):
        user = UserCreate(
            name="Arjun",
            email="ARJUN@example.com",
            password="Password123",
        )

        self.assertEqual(user.name, "Arjun")
        self.assertEqual(user.email, "arjun@example.com")

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
            PasswordResetConfirm(
                reset_token="a" * 20,
                new_password="password",
            )

    def test_password_reset_request_accepts_email(self):
        request = PasswordResetRequest(email="ARJUN@example.com")

        self.assertEqual(request.email, "arjun@example.com")


class PasswordResetSecurityTests(unittest.TestCase):
    def test_reset_token_contains_scoped_user_identity(self):
        token = create_password_reset_token(42, "stored-password-hash")
        payload = decode_password_reset_token(token)

        self.assertEqual(payload["sub"], "42")
        self.assertEqual(payload["purpose"], "password_reset")
        self.assertTrue(payload["jti"])
        self.assertNotEqual(payload["pwd"], "stored-password-hash")

    def test_reset_token_is_invalid_after_password_changes(self):
        token = create_password_reset_token(42, "old-password-hash")
        payload = decode_password_reset_token(token)

        self.assertTrue(
            reset_token_matches_password(payload, "old-password-hash")
        )
        self.assertFalse(
            reset_token_matches_password(payload, "new-password-hash")
        )

    def test_expired_reset_token_is_rejected(self):
        expired_token = jwt.encode(
            {
                "sub": "42",
                "purpose": "password_reset",
                "pwd": "fingerprint",
                "jti": "expired-token",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        with self.assertRaises(HTTPException) as context:
            decode_password_reset_token(expired_token)

        self.assertEqual(context.exception.status_code, 400)


class PasswordResetEndpointTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        User.__table__.create(self.engine)
        self.session_factory = sessionmaker(bind=self.engine)

        def override_get_db():
            database = self.session_factory()
            try:
                yield database
            finally:
                database.close()

        test_app = FastAPI()
        test_app.include_router(auth_router)
        test_app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(test_app)
        self.previous_debug = settings.DEBUG
        settings.DEBUG = True

        database = self.session_factory()
        database.add(
            User(
                name="Arjun",
                email="arjun@example.com",
                password_hash=hash_password("Password123"),
            )
        )
        database.commit()
        database.close()

    def tearDown(self):
        settings.DEBUG = self.previous_debug
        self.engine.dispose()

    def test_reset_request_does_not_reveal_account_existence(self):
        existing_response = self.client.post(
            "/auth/password-reset/request",
            json={"email": "arjun@example.com"},
        )
        missing_response = self.client.post(
            "/auth/password-reset/request",
            json={"email": "missing@example.com"},
        )

        self.assertEqual(existing_response.status_code, 200)
        self.assertEqual(missing_response.status_code, 200)
        self.assertEqual(
            existing_response.json()["message"],
            missing_response.json()["message"],
        )
        self.assertIn("reset_token", existing_response.json())
        self.assertNotIn("reset_token", missing_response.json())

    def test_reset_token_cannot_be_reused_after_password_change(self):
        request_response = self.client.post(
            "/auth/password-reset/request",
            json={"email": "arjun@example.com"},
        )
        token = request_response.json()["reset_token"]

        first_response = self.client.post(
            "/auth/password-reset/confirm",
            json={
                "reset_token": token,
                "new_password": "NewPassword456",
            },
        )
        second_response = self.client.post(
            "/auth/password-reset/confirm",
            json={
                "reset_token": token,
                "new_password": "AnotherPassword789",
            },
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 400)

        database = self.session_factory()
        user = database.query(User).filter_by(email="arjun@example.com").one()
        self.assertTrue(verify_password("NewPassword456", user.password_hash))
        database.close()

    def test_access_token_cannot_be_used_as_reset_token(self):
        access_style_token = jwt.encode(
            {
                "sub": "42",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        with self.assertRaises(HTTPException) as context:
            decode_password_reset_token(access_style_token)

        self.assertEqual(context.exception.status_code, 400)


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
