"""
Authentication router for API.

Provides endpoint for user login and JWT token generation.
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.services import user_service
from src.database.session import get_db
from src.security import oauth

router = APIRouter(tags=["Auth"])


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access and refresh tokens.

    :param form_data: Form data with username and password.
    :type form_data: OAuth2PasswordRequestForm
    :param session: SQLAlchemy session.
    :type session: Session
    :return: Access token and token type.
    :rtype: dict
    """
    from src.security.oauth import create_access_token
    user = user_service.authenticate_user(
        session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    access_token = create_access_token(
        {'sub': user.username, 'type': 'access'})
    refresh_token = create_access_token(
        {'sub': user.username, 'type': 'refresh', 'exp': datetime.now(timezone.utc) + timedelta(days=7)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_token(refresh_token: str, session: Session = Depends(get_db)):
    """
    Refresh access and refresh tokens using a valid refresh token.

    :param refresh_token: Refresh token obtained during login.
    :type refresh_token: str
    :param session: SQLAlchemy session.
    :type session: Session
    :return: New access and refresh tokens, and token type.
    :rtype: dict
    """
    from authlib.jose import jwt, JoseError
    from src.security.oauth import SECRET_KEY, create_access_token
    try:
        claims = jwt.decode(refresh_token, SECRET_KEY)
        claims.validate()
        if claims.get('type') != 'refresh':
            raise HTTPException(status_code=400, detail="Invalid token type")
        username = claims.get('sub')
    except JoseError:
        raise HTTPException(
            status_code=400, detail="Invalid or expired refresh token")
    user = user_service.get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_access_token = create_access_token(
        {'sub': user.username, 'type': 'access'})
    new_refresh_token = create_access_token(
        {'sub': user.username, 'type': 'refresh', 'exp': datetime.now(timezone.utc) + timedelta(days=7)})
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
