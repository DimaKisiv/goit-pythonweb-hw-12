"""
OAuth2 and JWT security utilities.

Provides functions for token creation, user authentication, and role validation.

:author: Your Name
:module: src.security.oauth
"""
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from authlib.jose import jwt, JoseError
from fastapi import HTTPException
from fastapi import status
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer


import os
from src.database.models import User, UserRole
from src.database.session import get_db
from src.database import user_repository

SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRES_IN_MINUTES = int(
    os.getenv('ACCESS_TOKEN_EXPIRES_IN_MINUTES', '30'))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token for the given data.

    :param data: Dictionary containing user data to encode in the token.
    :type data: dict
    :return: Encoded JWT access token as a string.
    :rtype: str
    """
    issue_date_time = datetime.now(timezone.utc)
    expire_date_time = issue_date_time + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN_MINUTES)
    header = {'alg': JWT_ALGORITHM}
    payload = {**data, "iat": issue_date_time, "exp": expire_date_time}
    return jwt.encode(header, payload, SECRET_KEY).decode('utf-8')


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Retrieve the current user from the JWT token.

    :param token: JWT access token from OAuth2 scheme.
    :type token: str
    :param db: SQLAlchemy database session.
    :type db: Session
    :return: User object if credentials are valid.
    :rtype: User
    :raises HTTPException: If credentials are invalid or user not found.
    """
    jwt_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        claims = jwt.decode(token, SECRET_KEY)
        claims.validate()
        username = claims.get('sub')
        if not username:
            raise jwt_exception
        user = user_repository.get_user_by_username(db, username)
        if not user:
            raise jwt_exception
        return user
    except JoseError as exc:
        raise jwt_exception from exc


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user is active.

    :param user: User object from dependency injection.
    :type user: User
    :return: The active User object.
    :rtype: User
    """
    return user


def get_current_active_admin(user: User = Depends(get_current_active_user)):
    """
    Ensure the current user has admin privileges.

    :param user: User object from dependency injection.
    :type user: User
    :return: The User object if admin.
    :rtype: User
    :raises HTTPException: If user is not an admin.
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User is not allowed to do this action")
    return user
