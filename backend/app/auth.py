# # app/auth.py
# ⚠️ SECURITY WARNING: Plain text passwords as requested

def generate_password_hash(password: str) -> str:
    # return plain password
    return password

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # simple string comparison
    return plain_password == hashed_password
