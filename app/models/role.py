from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from base import Base
from links import user_roles, role_permissions


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(256))

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles"
    )

    permission: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )