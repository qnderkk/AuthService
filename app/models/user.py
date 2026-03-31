from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .links import user_roles


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(64), unique=False, nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), unique=False, nullable=False)
    father_name: Mapped[str | None] = mapped_column(String(64), unique=False, index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin"
    )