"""
User service utilities for authentication, registration, and avatar management.

Provides functions for user creation, authentication, avatar updates, and email verification.

:author: Your Name
:module: src.services.user_service
"""
import cloudinary
import cloudinary.uploader
import os
import re
from sqlalchemy.orm import Session

from authlib.jose import jwt, JoseError
from fastapi import HTTPException
from fastapi import status
from src.database import user_repository
from src.security import passwords
from src.database.models import User, UserRole
from src.security.oauth import create_access_token


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def update_avatar(db: Session, user: User, file) -> str:
    """
    Update the user's avatar using Cloudinary.

    :param db: SQLAlchemy database session.
    :type db: Session
    :param user: User object whose avatar will be updated.
    :type user: User
    :param file: File object containing the new avatar image.
    :type file: Any
    :return: URL of the updated avatar image.
    :rtype: str
    """
    res = cloudinary.uploader.upload(
        file.file, folder="avatars", public_id=str(user.id), overwrite=True)
    user.avatar_url = res["secure_url"]
    db.commit()
    return user.avatar_url


def create_user(db: Session, username: str, password: str, role: UserRole) -> User:
    """
    Create a new user with the given credentials and role.

    :param db: SQLAlchemy database session.
    :type db: Session
    :param username: Username (must be a valid email address).
    :type username: str
    :param password: Plain text password.
    :type password: str
    :param role: Role for the new user.
    :type role: UserRole
    :return: The created User object.
    :rtype: User
    :raises HTTPException: If username is invalid or already exists.
    """
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", username):
        raise HTTPException(
            status_code=400, detail="Username must be a valid email address")
    existing = user_repository.get_user_by_username(db, username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    hashed_password = passwords.get_password_hash(password)
    user = user_repository.create_user(db, username, hashed_password, role)
    # oскільки в нас немає SMTP
    # Генеруємоі JWT токен для email-підтвердження, копіюємо його з консолі і вставляємо в verify-email ендпоінт
    token = create_access_token(
        {"sub": user.username, "action": "verify_email"})
    print(
        f"[FAKE EMAIL] To: {username} | Link: http://localhost:8000/verify-email/{token}")
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Retrieve a user by their username.

    :param db: SQLAlchemy database session.
    :type db: Session
    :param username: Username to search for.
    :type username: str
    :return: User object if found, else None.
    :rtype: User | None
    """
    return user_repository.get_user_by_username(db, username)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Authenticate a user by username and password.

    :param db: SQLAlchemy database session.
    :type db: Session
    :param username: Username to authenticate.
    :type username: str
    :param password: Plain text password to verify.
    :type password: str
    :return: User object if authentication succeeds, else None.
    :rtype: User | None
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not passwords.verify_password(password, user.password):
        return None
    return user


def verify_email_token(token: str, db: Session, secret_key: str) -> str:
    """
    Verify an email confirmation token and mark the user as verified.

    :param token: JWT token for email verification.
    :type token: str
    :param db: SQLAlchemy database session.
    :type db: Session
    :param secret_key: Secret key for decoding the token.
    :type secret_key: str
    :return: Confirmation message if verification succeeds.
    :rtype: str
    :raises HTTPException: If token is invalid, expired, or user not found.
    """
    try:
        claims = jwt.decode(token, secret_key)
        claims.validate()
        username = claims.get('sub')
        if claims.get('action') != 'verify_email':
            raise HTTPException(status_code=400, detail="Invalid token action")
    except JoseError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    return "Email verified!"
