import os
import secrets
import string
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Any, Union
from .config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that the plain text password matches the hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Returns a hashed version of the password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(subject: Union[str, Any], user_type: str, expires_delta: timedelta = None) -> str:
    """Creates a JWT token encoded with the user's ID (subject) and user_type."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject), "user_type": user_type}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def generate_otp(length: int = 6) -> str:
    """Generates a numeric OTP of the specified length."""
    return ''.join(secrets.choice(string.digits) for _ in range(length))
