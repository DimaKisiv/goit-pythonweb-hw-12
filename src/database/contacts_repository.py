from sqlalchemy.orm import Session
from src.database.models import Contact
from src.configuration.schemas import ContactCreate, ContactUpdate
from datetime import date, timedelta


def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of contacts for a user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param user_id: ID of the user.
    :type user_id: int
    :param skip: Number of records to skip.
    :type skip: int
    :param limit: Maximum number of records to return.
    :type limit: int
    :return: List of Contact objects.
    :rtype: list
    """
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Retrieve a single contact by ID for a user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param contact_id: ID of the contact.
    :type contact_id: int
    :param user_id: ID of the user.
    :type user_id: int
    :return: Contact object or None if not found.
    :rtype: Contact or None
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()


def create_contact(db: Session, contact: ContactCreate, user_id: int):
    """
    Create a new contact for a user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param contact: Contact creation schema.
    :type contact: ContactCreate
    :param user_id: ID of the user.
    :type user_id: int
    :return: The created Contact object.
    :rtype: Contact
    """
    db_contact = Contact(**contact.model_dump(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    """
    Update an existing contact for a user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param contact_id: ID of the contact.
    :type contact_id: int
    :param contact: Contact update schema.
    :type contact: ContactUpdate
    :param user_id: ID of the user.
    :type user_id: int
    :return: Updated Contact object or None if not found.
    :rtype: Contact or None
    """
    db_contact = db.query(Contact).filter(
        Contact.id == contact_id, Contact.user_id == user_id).first()
    if not db_contact:
        return None
    for field, value in contact.model_dump().items():
        setattr(db_contact, field, value)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Delete a contact for a user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param contact_id: ID of the contact.
    :type contact_id: int
    :param user_id: ID of the user.
    :type user_id: int
    :return: Deleted Contact object or None if not found.
    :rtype: Contact or None
    """
    db_contact = db.query(Contact).filter(
        Contact.id == contact_id, Contact.user_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def search_contacts(db: Session, user_id: int, first_name: str = None, last_name: str = None, email: str = None):
    """
    Search contacts by first name, last name, or email for a user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param user_id: ID of the user.
    :type user_id: int
    :param first_name: First name to search.
    :type first_name: str, optional
    :param last_name: Last name to search.
    :type last_name: str, optional
    :param email: Email to search.
    :type email: str, optional
    :return: List of matching Contact objects.
    :rtype: list
    """
    query = db.query(Contact).filter(Contact.user_id == user_id)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


def get_upcoming_birthdays(db: Session, user_id: int):
    """
    Get contacts with upcoming birthdays in the next 7 days for a user.

    :param db: SQLAlchemy session.
    :type db: Session
    :param user_id: ID of the user.
    :type user_id: int
    :return: List of Contact objects with upcoming birthdays.
    :rtype: list
    """
    today = date.today()
    next_week = today + timedelta(days=7)
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        Contact.birthday.between(today, next_week)
    ).all()
