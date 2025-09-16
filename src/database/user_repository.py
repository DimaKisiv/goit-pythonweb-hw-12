"""
User repository functions for database operations.

Provides functions to create and retrieve users from the database.
"""
from sqlalchemy.orm import Session

from src.database.models import User, UserRole


def create_user(db: Session, username: str, hashed_password: str, role: str) -> User:
    """
    Create a new user in the database.

    :param db: SQLAlchemy session.
    :type db: Session
    :param username: Username of the user.
    :type username: str
    :param hashed_password: Hashed password.
    :type hashed_password: str
    :param role: Role of the user.
    :type role: UserRole
    :return: The created User object.
    :rtype: User
    """
    user = User(username=username, password=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Retrieve a user by username.

    :param db: SQLAlchemy session.
    :type db: Session
    :param username: Username to search for.
    :type username: str
    :return: User object or None if not found.
    :rtype: User or None
    """
    return db.query(User).filter(User.username == username).first()
