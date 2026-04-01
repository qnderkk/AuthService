from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timezone, timedelta

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.schemas.auth import Token, RefreshTokenRequest
from app.models.token import RefreshToken
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email has already been registered."
        )
    
    new_user = User(
        email=user_in.email,
        name=user_in.name,
        last_name=user_in.last_name,
        father_name=user_in.father_name,
        hashed_password=hash_password(user_in.password)
    )

    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error when saving to the database"
        )
    
    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    db_refresh_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    db.add(db_refresh_token)
    try:
        await db.commit()
        await db.refresh(db_refresh_token)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error when saving to the database"
        )

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    query = select(RefreshToken).where(RefreshToken.token == refresh_data.refresh_token)
    result = await db.execute(query)
    token = result.scalar_one_or_none()

    payload = verify_token(refresh_data.refresh_token, access_type="refresh")

    if not token or token.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No such token exists"
        )
    
    access_token = create_access_token(data={"sub": str(payload.user_id)})
    refresh_token = create_refresh_token(data={"sub": str(payload.user_id)})

    db_refersh_token = RefreshToken(
        token=refresh_token,
        user_id=payload.user_id,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    db.add(db_refersh_token)
    try:
        await db.delete(token)
        await db.commit()
        await db.refresh(db_refersh_token)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error when saving to the database"
        )
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}