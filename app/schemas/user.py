from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator
from typing import Optional


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="Name of the user")
    last_name: str = Field(..., min_length=1, max_length=64, description="Last name of the user")
    father_name: Optional[str] = Field(None, min_length=1, max_length=64, description="Father name of the user")
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="The password must be at least 8 characters long")
    password_repeat: str = Field(..., min_length=8, description="The password must be at least 8 characters long")

    @model_validator(mode="after")
    def check_pass_match(self):
        if self.password != self.password_repeat:
            raise ValueError("Password do not match")
        return self


class UserRead(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    last_name: Optional[str] = None
    father_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)