from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router

from app.core.config import settings


app = FastAPI(title=settings.app_name)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "AuthService is active"}