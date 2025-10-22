"""
Script to create an admin user.
Usage: python scripts/create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime

from app.domain.entities import User, UserRole
from app.infrastructure.database.connection import AsyncSessionLocal
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.services.password_service import BcryptPasswordService


async def create_admin():
    """
    Create an admin user interactively.
    """
    print("=" * 60)
    print("Create Admin User")
    print("=" * 60)

    # Get user input
    email = input("Enter admin email: ").strip()
    password = input("Enter admin password: ").strip()
    first_name = input("Enter first name (optional): ").strip() or None
    last_name = input("Enter last name (optional): ").strip() or None

    # Validate input
    if not email or not password:
        print("Error: Email and password are required!")
        return

    if len(password) < 8:
        print("Error: Password must be at least 8 characters long!")
        return

    # Create session and services
    async with AsyncSessionLocal() as session:
        user_repo = SQLAlchemyUserRepository(session)
        password_service = BcryptPasswordService()

        # Check if user already exists
        existing_user = await user_repo.get_by_email(email)
        if existing_user:
            print(f"Error: User with email {email} already exists!")
            return

        # Create admin user
        admin_user = User(
            id=None,
            email=email,
            hashed_password=password_service.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=UserRole.ADMIN,
            is_verified=True,  # Auto-verify admin users
            verification_code=None,
            verification_code_expires_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Save to database
        created_user = await user_repo.create(admin_user)

        print("\n" + "=" * 60)
        print("Admin user created successfully!")
        print("=" * 60)
        print(f"ID: {created_user.id}")
        print(f"Email: {created_user.email}")
        print(f"Role: {created_user.role.value}")
        print(f"Verified: {created_user.is_verified}")
        print(f"Created at: {created_user.created_at}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(create_admin())
