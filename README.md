# Contacts API

A modern FastAPI backend for managing users and contacts, featuring JWT authentication, email verification, rate limiting, CORS, and avatar upload via Cloudinary. Designed for Docker Compose deployment with PostgreSQL.

## Features

- User registration and JWT login
- Email verification (with JWT link)
- Password hashing and secure authentication
- Avatar upload to Cloudinary
- CRUD for contacts
- Rate limiting (slowapi)
- CORS enabled for local development
- All secrets/configs via `.env`
- Modular router structure

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
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

- `POST /users` — Register user
- `POST /token` — Login (JWT)
- `GET /users/me` — Get current user (JWT required)
- `POST /users/avatar` — Upload avatar
- `POST /users/verify-email` — Send verification email
- `GET /users/verify/{token}` — Verify email
- `GET/POST/PUT/DELETE /contacts` — Manage contacts

### Database

- PostgreSQL runs in a Docker container.
- Data is stored in the `db_data` Docker volume.
- Tables are auto-created from SQLAlchemy models on startup.

### Migrations

- For schema changes, use Alembic (recommended for production).

### Development

- Hot reload enabled via Uvicorn.
- All code in `src/` folder, modular routers in `src/routers/`.

## License

MIT
