from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Response, Request

from app.api.deps import get_current_user
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.user import UserRead, UserUpdate
from app.db.session import get_db
from app.core.security import hash_password
from app.api.v1.utils import delete_auth_cookies


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
async def read_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/update", response_model=UserRead)
async def update_user(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = user_update.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(current_user, field, value)

    try:
        await db.commit()
        await db.refresh(current_user)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user data"
        )
    
    return current_user


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.is_active = False

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during account deactivation"
        )
    
    return None


@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        delete_auth_cookies(response)
        return {"message": "Already logout"}

    query = select(RefreshToken).where(RefreshToken.token == refresh_token)
    result = await db.execute(query)
    token = result.scalar_one_or_none()

    if token:
        try:
            await db.delete(token)
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Can not delete token from db"
            )

    delete_auth_cookies(response)

    return {"message": "Logged out successfully"}