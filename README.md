# Contacts API

A modern FastAPI backend for managing users and contacts, featuring:

- JWT authentication (access & refresh tokens)
- Email verification (JWT link)
- Password reset (request & confirm endpoints)
- Role-based access (admin/user)
- Avatar upload to Cloudinary (admin only)
- CRUD for contacts
- Rate limiting (slowapi)
- CORS enabled for local development
- All secrets/configs via `.env`
- Modular router structure
- In-memory SQLite database for tests

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL (Docker, production)
- SQLite (in-memory, tests)
- Authlib (JWT)
- slowapi (rate limiting)
- Cloudinary (avatars)
- Docker Compose

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Cloudinary account (for avatar uploads)

### Environment Variables

Create a `.env` file in the project root:

```
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_IN_MINUTES=30
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### Running with Docker Compose

```
docker-compose up --build
```

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

### API Endpoints

- `POST /users` — Register user (specify role: "user" or "admin")
- `POST /token` — Login (JWT access & refresh tokens)
- `POST /refresh` — Get new access & refresh tokens
- `GET /me` — Get current user (JWT required)
- `POST /users/avatar` — Upload avatar (admin only)
- `GET /verify-email/{token}` — Verify email
- `POST /users/request-password-reset` — Request password reset
- `POST /users/reset-password` — Confirm password reset
- `GET/POST/PUT/DELETE /contacts` — Manage contacts

### Database

- PostgreSQL runs in a Docker container (production).
- Data is stored in the `db_data` Docker volume.
- Tables are auto-created from SQLAlchemy models on startup.
- Tests use in-memory SQLite for isolation.

### Migrations

- For schema changes, use Alembic (recommended for production).

### Development & Testing

- Hot reload enabled via Uvicorn.
- All code in `src/` folder, modular routers in `src/routers/`.
- Run tests with:
  ```
  pytest
  ```
  (uses in-memory SQLite)

## License

MIT
