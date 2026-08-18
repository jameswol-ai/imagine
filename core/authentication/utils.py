import time
from typing import Dict
import jwt
from app.config import SECRET_KEY

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24  # 24 hours

def create_access_token(subject: str, expires_delta: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    now = int(time.time())
    payload: Dict[str, object] = {
        "sub": subject,
        "iat": now,
        "exp": now + expires_delta
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_access_token(token: str) -> Dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
