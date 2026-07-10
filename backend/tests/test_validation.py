import unittest

from fastapi import HTTPException
from pydantic import ValidationError

from app.schemas.user import UserCreate
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


if __name__ == "__main__":
    unittest.main()
