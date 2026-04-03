import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models import User, Role, Permission, user_roles, role_permissions
from app.core.security import hash_password

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("Очистка базы данных...")
        await db.execute(delete(user_roles))
        await db.execute(delete(role_permissions))
        await db.execute(delete(Permission))
        await db.execute(delete(Role))
        await db.execute(delete(User))
        
        print("Создание прав...")
        perms_data = [
            Permission(name="users_view", description="Просмотр списка пользователей"),
            Permission(name="users_edit", description="Редактирование данных пользователей"),
            Permission(name="users_delete", description="Удаление пользователей"),
            Permission(name="roles_manage", description="Управление ролями и правами"),
        ]

        print("Создание ролей...")
        admin_role = Role(
            name="admin", 
            description="Полный доступ",
            permissions=perms_data
        )
        user_role = Role(
            name="user", 
            description="Обычный пользователь",
            permissions=[perms_data[0]]
        )
        
        db.add_all([admin_role, user_role])
        await db.flush() 

        print("Создание пользователей...")
        users = [
            User(
                email="roma@gmail.com",
                hashed_password=hash_password("admin123"),
                is_active=True,
                name="Роман",
                last_name="Иванов",
                roles=[admin_role]
            ),
            User(
                email="lena@gmail.com",
                hashed_password=hash_password("user123"),
                is_active=True,
                name="Лена",
                last_name="Иванова",
                roles=[user_role]
            ),
            User(
                email="alex@gmail.com",
                hashed_password=hash_password("alex123"),
                is_active=True,
                name="Alex",
                last_name="Ivanov",
                roles=[user_role]
            ),
        ]
        db.add_all(users)
        
        await db.commit()
        print("База успешно заполнена тестовыми данными!")

if __name__ == "__main__":
    asyncio.run(seed_data())