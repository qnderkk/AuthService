from passlib.context import CryptContext

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.auth import TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "scope": "access"
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "scope": "refresh"
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str, access_type: str = "access") -> TokenData | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)

        token_type = payload.get("scope")
        if token_type != access_type:
            raise ValueError("Invalid token type")
        
        token_data = TokenData(
            user_id=int(payload.get("sub")),
            email=payload.get("email"),
            scope=payload.get("scope") 
        )

        if token_data.user_id is None:
            raise ValueError("Token missing subject")
        
        return token_data
        
    except (JWTError, ValueError):
        return None

