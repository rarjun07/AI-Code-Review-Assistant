import unittest
from unittest.mock import patch

from app.services.password_reset_rate_limit_service import PasswordResetRateLimiter


class PasswordResetRateLimiterTests(unittest.TestCase):
    def test_rejects_requests_after_email_limit(self):
        limiter = PasswordResetRateLimiter()

        with (
            patch(
                "app.services.password_reset_rate_limit_service.settings."
                "PASSWORD_RESET_RATE_LIMIT_EMAIL",
                2,
            ),
            patch(
                "app.services.password_reset_rate_limit_service.settings."
                "PASSWORD_RESET_RATE_LIMIT_IP",
                10,
            ),
        ):
            self.assertTrue(limiter.allow("arjun@example.com", "127.0.0.1"))
            self.assertTrue(limiter.allow("arjun@example.com", "127.0.0.1"))
            self.assertFalse(limiter.allow("arjun@example.com", "127.0.0.1"))


if __name__ == "__main__":
    unittest.main()
