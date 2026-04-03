from fastapi import Depends, HTTPException, status

from app.api.deps import get_current_user
from app.models.user import User


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    def __call__(self, user: User = Depends(get_current_user)):
        user_permissions = []
        for role in user.roles:
            for perm in role.permissions:
                user_permissions.append(perm.name)
        
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have roots for: {self.required_permission}"
            )
        
        return user