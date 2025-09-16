"""
Authentication router for API.

Provides endpoint for user login and JWT token generation.
"""
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
    Authenticate user and return JWT access token.

    :param form_data: Form data with username and password.
    :type form_data: OAuth2PasswordRequestForm
    :param session: SQLAlchemy session.
    :type session: Session
    :return: Access token and token type.
    :rtype: dict
    """
    user = user_service.authenticate_user(
        session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password")
    access_token = oauth.create_access_token({'sub': user.username})
    return {"access_token": access_token, "token_type": "bearer"}
