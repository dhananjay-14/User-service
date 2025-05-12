from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext
from app.common.config.config import settings

# JWT settings
SECRET_KEY   = settings.secret_key      
ALGORITHM    = settings.jwt_algorithm   
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash a raw password using bcrypt
def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)

# Verify if a raw password matches its hashed version
def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)

# Create a JWT access token with optional expiration
def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decode and verify a JWT access token
def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
