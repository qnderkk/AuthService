from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base import Base
from links import role_permissions


class Permission(Base):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(256))

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions,
        back_populates="permissions"
    )