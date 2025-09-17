"""
Schemas for contacts and users.

This module defines Pydantic models for contacts and users, used for validation and serialization in the API.
"""
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from pydantic import ConfigDict

from src.database.models import UserRole


class ContactBase(BaseModel):
    """
    Base schema for a contact.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    extra_data: Optional[str] = None


class ContactCreate(ContactBase):
    """
    Schema for creating a new contact.
    """
    pass


class ContactUpdate(ContactBase):
    """
    Schema for updating an existing contact.
    """
    pass


class ContactOut(ContactBase):
    """
    Output schema for a contact, including ID.
    """
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """
    username: str
    password: str
    role: str = "USER"


class UserRead(BaseModel):
    """
    Output schema for user data.
    """
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
