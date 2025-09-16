"""
User router for API.

Provides endpoints for user registration, profile, avatar upload, and email verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, File, UploadFile, Request
from sqlalchemy.orm import Session
from src.configuration.schemas import UserCreate, UserRead
from src.services import user_service
from src.database.session import get_db
from src.security import oauth
from src.security.oauth import SECRET_KEY
from src.services.user_service import verify_email_token, update_avatar
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(tags=["User"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(user_create: UserCreate, session: Session = Depends(get_db)):
    """
    Create a new user.

    :param user_create: User creation schema.
    :type user_create: UserCreate
    :param session: SQLAlchemy session.
    :type session: Session
    :return: Created user.
    :rtype: UserRead
    """
    user = user_service.create_user(
        session, user_create.username, user_create.password, role="USER")
    return user


@router.get("/me")
@limiter.limit("5/minute")
def get_me(request: Request, current_user=Depends(oauth.get_current_user)):
    """
    Get current authenticated user profile.

    :param request: FastAPI request object.
    :type request: Request
    :param current_user: Current authenticated user.
    :return: Current user object.
    :rtype: UserRead
    """
    return current_user


@router.post("/users/avatar")
def upload_avatar(current_user=Depends(oauth.get_current_user), db: Session = Depends(get_db), file: UploadFile = File(...)):
    """
    Upload avatar for the current user.

    :param current_user: Current authenticated user.
    :param db: SQLAlchemy session.
    :type db: Session
    :param file: Uploaded avatar file.
    :type file: UploadFile
    :return: Avatar URL.
    :rtype: dict
    """
    url = update_avatar(db, current_user, file)
    return {"avatar_url": url}


@router.get("/verify-email/{token}")
def verify_email(token: str, session: Session = Depends(get_db)):
    """
    Verify user email using token.

    :param token: Email verification token.
    :type token: str
    :param session: SQLAlchemy session.
    :type session: Session
    :return: Verification message.
    :rtype: dict
    """
    message = verify_email_token(token, session, SECRET_KEY)
    return {"message": message}
