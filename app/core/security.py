import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(subject: int, expires_delta: Optional[timedelta] = None, secret_key: str = "") -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60 * 24 * 7))
    to_encode = {"exp": expire, "sub": str(subject)}
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
