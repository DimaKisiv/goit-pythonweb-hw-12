"""
Contacts router for API.

Provides endpoints for CRUD operations and search on contacts.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from src.configuration.schemas import ContactOut, ContactCreate, ContactUpdate
from src.database import contacts_repository
from src.database.session import get_db
from src.security import oauth

router = APIRouter(tags=["Contacts"])


@router.post("/contacts/", response_model=ContactOut, status_code=201)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    """
    Create a new contact for the current user.

    :param contact: Contact creation schema.
    :type contact: ContactCreate
    :param db: SQLAlchemy session.
    :type db: Session
    :param current_user: Current authenticated user.
    :return: Created contact.
    :rtype: ContactOut
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return contacts_repository.create_contact(db=db, contact=contact, user_id=current_user.id)


@router.get("/contacts/", response_model=list[ContactOut])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    """
    Retrieve all contacts for the current user.

    :param skip: Number of records to skip.
    :type skip: int
    :param limit: Maximum number of records to return.
    :type limit: int
    :param db: SQLAlchemy session.
    :type db: Session
    :param current_user: Current authenticated user.
    :return: List of contacts.
    :rtype: list[ContactOut]
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return contacts_repository.get_contacts(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/contacts/{contact_id}", response_model=ContactOut)
def read_contact(contact_id: int, db: Session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    """
    Retrieve a contact by ID for the current user.

    :param contact_id: ID of the contact.
    :type contact_id: int
    :param db: SQLAlchemy session.
    :type db: Session
    :param current_user: Current authenticated user.
    :return: Contact object.
    :rtype: ContactOut
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    db_contact = contacts_repository.get_contact(
        db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/contacts/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    """
    Update a contact for the current user.

    :param contact_id: ID of the contact.
    :type contact_id: int
    :param contact: Contact update schema.
    :type contact: ContactUpdate
    :param db: SQLAlchemy session.
    :type db: Session
    :param current_user: Current authenticated user.
    :return: Updated contact.
    :rtype: ContactOut
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    db_contact = contacts_repository.update_contact(
        db, contact_id=contact_id, contact=contact, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.delete("/contacts/{contact_id}", response_model=ContactOut)
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    """
    Delete a contact for the current user.

    :param contact_id: ID of the contact.
    :type contact_id: int
    :param db: SQLAlchemy session.
    :type db: Session
    :param current_user: Current authenticated user.
    :return: Deleted contact.
    :rtype: ContactOut
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    db_contact = contacts_repository.delete_contact(
        db, contact_id=contact_id, user_id=current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get("/contacts/search/", response_model=list[ContactOut])
def search_contacts(first_name: str | None = None, last_name: str | None = None, email: str | None = None, db: Session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    """
    Search contacts for the current user by first name, last name, or email.

    :param first_name: First name to search.
    :type first_name: str, optional
    :param last_name: Last name to search.
    :type last_name: str, optional
    :param email: Email to search.
    :type email: str, optional
    :param db: SQLAlchemy session.
    :type db: Session
    :param current_user: Current authenticated user.
    :return: List of matching contacts.
    :rtype: list[ContactOut]
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return contacts_repository.search_contacts(db, user_id=current_user.id, first_name=first_name, last_name=last_name, email=email)


@router.get("/contacts/upcoming_birthdays/", response_model=list[ContactOut])
def upcoming_birthdays(db: Session = Depends(get_db), current_user=Depends(oauth.get_current_user)):
    """
    Get contacts with upcoming birthdays for the current user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param current_user: Current authenticated user.
    :return: List of contacts with upcoming birthdays.
    :rtype: list[ContactOut]
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return contacts_repository.get_upcoming_birthdays(db, user_id=current_user.id)
