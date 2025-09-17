"""
User router for API.

Provides endpoints for user registration, profile, avatar upload, and email verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, File, UploadFile, Request, Body
from sqlalchemy.orm import Session
from src.configuration.schemas import UserCreate, UserRead, PasswordResetConfirm, PasswordResetRequest
from src.services import user_service
from src.database.session import get_db
from src.security import oauth
from src.security.oauth import SECRET_KEY, create_access_token
from src.services.user_service import verify_email_token, update_avatar
from src.security.passwords import get_password_hash
from slowapi import Limiter
from slowapi.util import get_remote_address
from authlib.jose import jwt, JoseError
from src.database.models import UserRole


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
    if user_create.role not in (UserRole.USER, UserRole.ADMIN):
        raise HTTPException(
            status_code=400, detail=f"Invalid role: {user_create.role}")
    user = user_service.create_user(
        session, user_create.username, user_create.password, role=user_create.role)
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
    Upload avatar for the current user. Only admins can change their own avatar if they are the default admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admin can change their own avatar.")
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


@router.post("/users/request-password-reset")
def request_password_reset(data: PasswordResetRequest = Body(...), session: Session = Depends(get_db)):
    user = user_service.get_user_by_username(session, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = create_access_token(
        {"sub": user.username, "action": "reset_password"})
    # send email with token and link to reset password
    return {"reset_token": token}


@router.post("/users/reset-password")
def reset_password(data: PasswordResetConfirm = Body(...), session: Session = Depends(get_db)):
    try:
        claims = jwt.decode(data.token, SECRET_KEY)
        claims.validate()
        username = claims.get('sub')
        if claims.get('action') != 'reset_password':
            raise HTTPException(status_code=400, detail="Invalid token action")
    except JoseError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = user_service.get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password = get_password_hash(data.new_password)
    session.commit()
    return {"message": "Password reset successful"}
