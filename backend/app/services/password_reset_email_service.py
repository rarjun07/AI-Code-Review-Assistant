import logging
from urllib.parse import urlencode

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

RESEND_EMAIL_ENDPOINT = "https://api.resend.com/emails"


def build_password_reset_url(reset_token: str) -> str:
    query = urlencode({"token": reset_token})
    return f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?{query}"


def send_password_reset_email(recipient: str, reset_token: str) -> bool:
    """Send a password reset link without logging the address or token."""
    if settings.PASSWORD_RESET_EMAIL_PROVIDER != "resend":  # nosec B105
        return False

    if not settings.RESEND_API_KEY or not settings.PASSWORD_RESET_FROM_EMAIL:
        logger.error("Password reset email provider is not fully configured")
        return False

    reset_url = build_password_reset_url(reset_token)
    response = httpx.post(
        RESEND_EMAIL_ENDPOINT,
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "User-Agent": f"{settings.APP_NAME}/{settings.VERSION}",
        },
        json={
            "from": settings.PASSWORD_RESET_FROM_EMAIL,
            "to": [recipient],
            "subject": "Reset your AI Code Review password",
            "text": (
                "Use the link below to reset your password. "
                f"It expires in {settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.\n\n"
                f"{reset_url}\n\n"
                "If you did not request this reset, you can ignore this email."
            ),
        },
        timeout=10.0,
    )
    response.raise_for_status()
    return True
