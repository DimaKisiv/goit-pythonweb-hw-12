"""
Integration tests for FastAPI routes using pytest and TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.configuration.schemas import ContactCreate

client = TestClient(app)


def get_token():
    # Register user if not exists
    client.post(
        "/users", json={"username": "testuser@example.com", "password": "testpass"})
    # Login and get token
    response = client.post(
        "/token", data={"username": "testuser@example.com", "password": "testpass"})
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_create_user():
    payload = {"username": "testuser@example.com", "password": "testpass"}
    response = client.post("/users", json=payload)
    assert response.status_code in (200, 201, 409)


def test_token():
    # Try to get a token (login)
    response = client.post(
        "/token", data={"username": "testuser@example.com", "password": "testpass"})
    assert response.status_code in (200, 401)


def test_create_contact():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    contact = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "birthday": "2000-01-01",
        "extra_data": None
    }
    response = client.post("/contacts/", json=contact, headers=headers)
    assert response.status_code == 201
    assert response.json()["first_name"] == "John"


def test_read_contacts():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/contacts/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_contact():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    # Create contact
    contact = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "9876543210",
        "birthday": "1990-05-05",
        "extra_data": None
    }
    create_resp = client.post("/contacts/", json=contact, headers=headers)
    contact_id = create_resp.json()["id"]
    # Update contact
    update = contact.copy()
    update["first_name"] = "Janet"
    response = client.put(
        f"/contacts/{contact_id}", json=update, headers=headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Janet"


def test_delete_contact():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    # Create contact
    contact = {
        "first_name": "Delete",
        "last_name": "Me",
        "email": "delete.me@example.com",
        "phone": "5555555555",
        "birthday": "1985-12-12",
        "extra_data": None
    }
    create_resp = client.post("/contacts/", json=contact, headers=headers)
    contact_id = create_resp.json()["id"]
    # Delete contact
    response = client.delete(f"/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == contact_id


def test_search_contacts():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/contacts/search/?first_name=John", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_upcoming_birthdays():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/contacts/upcoming_birthdays/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_me_unauth():
    response = client.get("/me")
    assert response.status_code == 401


def test_contacts_list_unauth():
    response = client.get("/contacts/")
    assert response.status_code == 401

# Add avatar and email verification tests as needed
