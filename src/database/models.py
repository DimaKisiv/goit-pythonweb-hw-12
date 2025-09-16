"""
SQLAlchemy models for contacts and users.

Defines database tables and user roles for the application.
"""
from enum import Enum, auto
from sqlalchemy import Column, Integer, String, Date
from src.database.session import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Contact(Base):
    """
    SQLAlchemy model for a contact.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    birthday = Column(Date, index=True)
    extra_data = Column(String, nullable=True)
    user_id = Column(Integer, index=True)  # owner id


class UserRole:
    """
    User role constants.
    """
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    """
    SQLAlchemy model for a user.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default=UserRole.USER)
    is_verified: Mapped[bool] = mapped_column(default=False)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        """
        String representation of the User object.
        """
        return f"User(id={self.id!r}, username={self.password})"
