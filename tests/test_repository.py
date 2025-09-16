"""
Tests for repository layer using in-memory SQLite database.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, User, UserRole, Contact
from src.database import user_repository, contacts_repository
from src.security import passwords
from src.configuration.schemas import ContactCreate


@pytest.fixture(scope="function")
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

# User repository tests


def test_create_and_get_user(in_memory_db):
    db = in_memory_db
    username = "test@example.com"
    password = "password123"
    role = UserRole.USER
    hashed_password = passwords.get_password_hash(password)
    user = user_repository.create_user(db, username, hashed_password, role)
    assert user.username == username
    assert user.role == role
    fetched = user_repository.get_user_by_username(db, username)
    assert fetched is not None
    assert fetched.username == username


def test_user_not_found(in_memory_db):
    db = in_memory_db
    user = user_repository.get_user_by_username(db, "notfound@example.com")
    assert user is None


def test_update_user(in_memory_db):
    db = in_memory_db
    username = "update@example.com"
    password = passwords.get_password_hash("pass")
    user = user_repository.create_user(db, username, password, UserRole.USER)
    user.password = passwords.get_password_hash("newpass")
    db.commit()
    updated = user_repository.get_user_by_username(db, username)
    assert passwords.verify_password("newpass", updated.password)


def test_delete_user(in_memory_db):
    db = in_memory_db
    username = "delete@example.com"
    password = passwords.get_password_hash("pass")
    user = user_repository.create_user(db, username, password, UserRole.USER)
    db.delete(user)
    db.commit()
    deleted = user_repository.get_user_by_username(db, username)
    assert deleted is None


# Contacts repository tests


def test_create_and_get_contact(in_memory_db):
    db = in_memory_db
    username = "contactuser@example.com"
    password = passwords.get_password_hash("pass")
    user = user_repository.create_user(db, username, password, UserRole.USER)
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday="2000-01-01",
        extra_data=None
    )
    contact = contacts_repository.create_contact(db, contact_data, user.id)
    assert contact.first_name == "John"
    assert contact.user_id == user.id
    fetched = contacts_repository.get_contact(db, contact.id, user.id)
    assert fetched is not None
    assert fetched.email == "john@example.com"


def test_contact_not_found(in_memory_db):
    db = in_memory_db
    # Create user for user_id context
    username = "notfounduser@example.com"
    password = passwords.get_password_hash("pass")
    user = user_repository.create_user(db, username, password, UserRole.USER)
    contact = contacts_repository.get_contact(db, 999, user.id)
    assert contact is None


def test_get_contacts(in_memory_db):
    db = in_memory_db
    username = "listcontacts@example.com"
    password = passwords.get_password_hash("pass")
    user = user_repository.create_user(db, username, password, UserRole.USER)
    for i in range(3):
        contact_data = ContactCreate(
            first_name=f"First{i}",
            last_name=f"Last{i}",
            email=f"email{i}@example.com",
            phone=f"12345{i}",
            birthday="2000-01-01",
            extra_data=None
        )
        contacts_repository.create_contact(db, contact_data, user.id)
    result = contacts_repository.get_contacts(db, user.id)
    assert len(result) == 3


def test_update_contact(in_memory_db):
    db = in_memory_db
    username = "updatecontact@example.com"
    password = passwords.get_password_hash("pass")
    user = user_repository.create_user(db, username, password, UserRole.USER)
    contact_data = ContactCreate(
        first_name="First",
        last_name="Last",
        email="email@example.com",
        phone="12345",
        birthday="2000-01-01",
        extra_data=None
    )
    contact = contacts_repository.create_contact(db, contact_data, user.id)
    update_data = ContactCreate(
        first_name="Updated",
        last_name="Last",
        email="email@example.com",
        phone="12345",
        birthday="2000-01-01",
        extra_data=None
    )
    updated = contacts_repository.update_contact(
        db, contact.id, update_data, user.id)
    assert updated.first_name == "Updated"


def test_delete_contact(in_memory_db):
    db = in_memory_db
    username = "deletecontact@example.com"
    password = passwords.get_password_hash("pass")
    user = user_repository.create_user(db, username, password, UserRole.USER)
    contact_data = ContactCreate(
        first_name="First",
        last_name="Last",
        email="email@example.com",
        phone="12345",
        birthday="2000-01-01",
        extra_data=None
    )
    contact = contacts_repository.create_contact(db, contact_data, user.id)
    deleted = contacts_repository.delete_contact(db, contact.id, user.id)
    assert deleted is not None
    assert contacts_repository.get_contact(db, contact.id, user.id) is None

# Add more CRUD tests as needed
