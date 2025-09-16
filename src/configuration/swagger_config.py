"""
Swagger/OpenAPI configuration for FastAPI application.

Defines tags metadata and OpenAPI keyword arguments for API documentation.
"""
tags_metadata = [
    {"name": "Auth", "description": "Authentication and token management."},
    {"name": "User", "description": "User registration, profile, avatar, verification."},
    {"name": "Contacts", "description": "CRUD operations over contacts."},
    {"name": "Search",   "description": "Search by name/email and upcoming birthdays."},
]

OPENAPI_KWARGS = dict(
    title="Contacts REST API",
    description=(
        "FastAPI + SQLAlchemy + PostgreSQL.\n\n"
        "Features: CRUD, search by first/last name or email, upcoming birthdays (7 days)."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={"name": "HW8 Support", "url": "https://example.com",
             "email": "support@example.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)
