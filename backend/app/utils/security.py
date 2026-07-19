import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def password_hash_fingerprint(password_hash: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        password_hash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_password_reset_token(user_id: int, password_hash: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )

    return jwt.encode(
        {
            "sub": str(user_id),
            "purpose": "password_reset",
            "pwd": password_hash_fingerprint(password_hash),
            "jti": uuid4().hex,
            "iat": datetime.now(timezone.utc),
            "exp": expire,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_password_reset_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset link is invalid or has expired",
        ) from exc

    if (
        payload.get("purpose") != "password_reset"
        or not str(payload.get("sub", "")).isdigit()
        or not payload.get("pwd")
        or not payload.get("jti")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset link is invalid or has expired",
        )

    return payload


def reset_token_matches_password(payload: dict, password_hash: str) -> bool:
    return hmac.compare_digest(
        str(payload.get("pwd", "")),
        password_hash_fingerprint(password_hash),
    )



def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
