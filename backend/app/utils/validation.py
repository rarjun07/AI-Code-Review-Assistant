import re
from pathlib import Path

from fastapi import HTTPException, status


MAX_UPLOAD_SIZE_BYTES = 1024 * 1024
ALLOWED_EXTENSIONS = {".py"}


def sanitize_filename(filename: str) -> str:
    name = Path(filename or "").name.strip()
    name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)

    if not name or name in {".", ".."}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename",
        )

    return name


def validate_python_upload(filename: str, content: bytes) -> str:
    safe_filename = sanitize_filename(filename)
    extension = Path(safe_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Python .py files are allowed",
        )

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file is too large. Maximum size is 1 MB",
        )

    return safe_filename
