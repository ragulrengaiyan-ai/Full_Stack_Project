# app/auth.py
import json
import hmac
import hashlib
import base64
import time
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models import User

# Secret key for signing (in a real app, this should be in .env)
SECRET_KEY = "my_super_secret_key_for_this_project_123"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/users/login", auto_error=False)

def base64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64_url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta
    else:
        expire = time.time() + 24 * 3600 # 24 hours default
    
    to_encode.update({"exp": expire})
    
    # 1. Header
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header).encode('utf-8')
    header_b64 = base64_url_encode(header_json)
    
    # 2. Payload
    payload_json = json.dumps(to_encode).encode('utf-8')
    payload_b64 = base64_url_encode(payload_json)
    
    # 3. Signature
    signature_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), signature_input, hashlib.sha256).digest()
    signature_b64 = base64_url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_token(token: str):
    try:
        parts = token.split('.')
        if len(parts) != 3:
             raise HTTPException(status_code=401, detail="Invalid token format")
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        signature_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), signature_input, hashlib.sha256).digest()
        expected_signature_b64 = base64_url_encode(expected_signature)
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
             raise HTTPException(status_code=401, detail="Invalid token signature")
             
        # Decode payload
        payload_json = base64_url_decode(payload_b64).decode('utf-8')
        payload = json.loads(payload_json)
        
        # Check expiration
        if "exp" in payload and payload["exp"] < time.time():
             raise HTTPException(status_code=401, detail="Token expired")
             
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except HTTPException:
         raise
    except Exception: # Catch any other unexpected errors during token processing
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
        
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            return None
        return db.query(User).filter(User.email == email).first()
    except Exception:
        return None

def generate_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
