from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def refresh_token(token: str) -> Optional[str]:
    payload = decode_token(token)
    if not payload:
        return None
    exp = payload.get("exp")
    if not exp:
        return None
    exp_datetime = datetime.fromtimestamp(exp)
    if datetime.utcnow() > exp_datetime:
        return None
    new_exp = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload.update({"exp": new_exp})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_psychologist_token(psychologist: dict) -> str:
    email = psychologist.get("email")
    if isinstance(email, list):
        email = email[0] if email else ""
    else:
        email = email or ""
    return create_access_token(
        {"sub": str(psychologist["_id"]), "email": email},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    )


def generate_edit_token(event_id: str, psychologist_id: str, client_email: str | None = None) -> str:
    payload = {
        "event_id": event_id,
        "psychologist_id": psychologist_id,
    }
    if client_email:
        payload["client_email"] = client_email
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_edit_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
