#!/usr/bin/env python3
"""
Create Initial Admin User
Run this script once after initial database setup
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.auth import UserCreate
from app.services.auth_service import AuthService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user():
    """Create the initial admin user from environment variables"""

    db = SessionLocal()

    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()

        if existing_admin:
            logger.warning(f"Admin user '{settings.ADMIN_USERNAME}' already exists!")
            logger.info(f"User ID: {existing_admin.id}")
            logger.info(f"Email: {existing_admin.email}")
            logger.info(f"Role: {existing_admin.role}")
            logger.info(f"Active: {existing_admin.is_active}")
            return existing_admin

        # Create admin user
        logger.info("Creating initial admin user...")

        user_data = UserCreate(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            full_name=settings.ADMIN_FULL_NAME,
            role="admin",
        )

        admin_user = AuthService.create_user(db, user_data)

        logger.info("=" * 80)
        logger.info("✓ Admin user created successfully!")
        logger.info("=" * 80)
        logger.info(f"Username: {admin_user.username}")
        logger.info(f"Email: {admin_user.email}")
        logger.info(f"Full Name: {admin_user.full_name}")
        logger.info(f"Role: {admin_user.role}")
        logger.info(f"User ID: {admin_user.id}")
        logger.info("=" * 80)
        logger.info("")
        logger.info("⚠️  IMPORTANT: Change the admin password immediately!")
        logger.info("")
        logger.info("Login credentials:")
        logger.info(f"  Username: {settings.ADMIN_USERNAME}")
        logger.info(f"  Password: {settings.ADMIN_PASSWORD}")
        logger.info("")
        logger.info("Login URL: http://localhost:8000/docs")
        logger.info("")
        logger.info("=" * 80)

        return admin_user

    except Exception as e:
        logger.error(f"Error creating admin user: {e}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    try:
        create_admin_user()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        sys.exit(1)
