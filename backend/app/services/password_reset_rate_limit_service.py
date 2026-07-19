import hashlib
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from app.config import settings


class PasswordResetRateLimiter:
    """Small in-process limiter suitable for the single-instance demo service."""

    def __init__(self) -> None:
        self._attempts: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = threading.Lock()

    @staticmethod
    def _email_key(email: str) -> str:
        digest = hashlib.sha256(email.encode("utf-8")).hexdigest()
        return f"email:{digest}"

    def _consume(self, key: str, limit: int, now: datetime) -> bool:
        cutoff = now - timedelta(
            minutes=settings.PASSWORD_RESET_RATE_LIMIT_WINDOW_MINUTES
        )
        attempts = self._attempts[key]

        while attempts and attempts[0] <= cutoff:
            attempts.popleft()

        if len(attempts) >= limit:
            return False

        attempts.append(now)
        return True

    def allow(self, email: str, client_ip: str) -> bool:
        now = datetime.now(timezone.utc)

        with self._lock:
            email_allowed = self._consume(
                self._email_key(email),
                settings.PASSWORD_RESET_RATE_LIMIT_EMAIL,
                now,
            )
            ip_allowed = self._consume(
                f"ip:{client_ip}",
                settings.PASSWORD_RESET_RATE_LIMIT_IP,
                now,
            )

        return email_allowed and ip_allowed

    def clear(self) -> None:
        with self._lock:
            self._attempts.clear()


password_reset_rate_limiter = PasswordResetRateLimiter()
