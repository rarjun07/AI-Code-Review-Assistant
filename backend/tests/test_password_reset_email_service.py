import unittest
from unittest.mock import Mock, patch

from app.services.password_reset_email_service import (
    build_password_reset_url,
    send_password_reset_email,
)


class PasswordResetEmailServiceTests(unittest.TestCase):
    def test_reset_url_points_to_frontend(self):
        with patch(
            "app.services.password_reset_email_service.settings.FRONTEND_URL",
            "https://review.example.com/",
        ):
            url = build_password_reset_url("header.payload.signature")

        self.assertEqual(
            url,
            "https://review.example.com/reset-password?token="
            "header.payload.signature",
        )

    @patch("app.services.password_reset_email_service.httpx.post")
    def test_resend_delivery_uses_authorized_https_request(self, post):
        response = Mock()
        post.return_value = response

        with (
            patch(
                "app.services.password_reset_email_service.settings."
                "PASSWORD_RESET_EMAIL_PROVIDER",
                "resend",
            ),
            patch(
                "app.services.password_reset_email_service.settings."
                "RESEND_API_KEY",
                "re_test_key",
            ),
            patch(
                "app.services.password_reset_email_service.settings."
                "PASSWORD_RESET_FROM_EMAIL",
                "AI Review <reset@example.com>",
            ),
            patch(
                "app.services.password_reset_email_service.settings.FRONTEND_URL",
                "https://review.example.com",
            ),
        ):
            sent = send_password_reset_email(
                "arjun@example.com",
                "header.payload.signature",
            )

        self.assertTrue(sent)
        response.raise_for_status.assert_called_once_with()
        request = post.call_args
        self.assertEqual(request.args[0], "https://api.resend.com/emails")
        self.assertEqual(
            request.kwargs["headers"]["Authorization"],
            "Bearer re_test_key",
        )
        self.assertEqual(request.kwargs["json"]["to"], ["arjun@example.com"])


if __name__ == "__main__":
    unittest.main()
