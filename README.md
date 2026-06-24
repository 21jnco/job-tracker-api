# Job Tracker API
 
A backend REST API for tracking job applications and their associated notes, built with FastAPI and PostgreSQL. The project implements JWT-based authentication, per-user data isolation, and a soft-delete system with cascade behavior.
 
> This is a learning project focused on building a clean, well-structured backend with production-style patterns (layered architecture, dependency injection, automated tests).
 
<!-- TODO: if you deploy it, add a live link here, e.g.:
**Live demo:** https://your-app.onrender.com/docs -->
 
---
 
## Features
 
- **Authentication** — user registration and login via OAuth2 password flow, with JWT access tokens.
- **Job applications** — full CRUD (create, read, update, delete) with status tracking (applied / interview / offer / rejected).
- **Notes** — notes attached to job applications (nested resource), with full CRUD.
- **Per-user data isolation** — every query is scoped to the authenticated user; one user can never read or modify another user's data.
- **Soft delete** — records are never physically removed; they are marked with a `deleted_at` timestamp and hidden from normal queries.
- **Cascade soft-delete** — deleting a job application also soft-deletes its notes (tracked via a `delete_with_parent` flag).
- **Recovery** — soft-deleted job applications can be restored, which also restores notes that were deleted together with the application.
- **Pagination** — list endpoints support `limit` / `offset` pagination.
- **Timezone-aware timestamps** — `created_at`, `updated_at`, and `deleted_at` are stored in UTC.
<!-- TODO: remove or adjust any feature above that doesn't match what you actually shipped -->
 
---
 
## Tech stack
 
| Area            | Technology                          |
|-----------------|-------------------------------------|
| Language        | Python 3.14                         |
| Web framework   | FastAPI                             |
| Validation      | Pydantic                            |
| Database        | PostgreSQL                          |
| ORM             | SQLAlchemy 2.0                      |
| Migrations      | Alembic                             |
| Auth            | JWT (python-jose), passlib / bcrypt |
| Testing         | pytest                              |
 
---
 
## Architecture
 
The project follows a layered architecture to keep responsibilities separated and the code testable:
 
```
app/
├── api/
│   └── routers/        # HTTP layer: thin endpoints that delegate to services
├── core/               # Config, database setup, security, error messages
├── dependencies/       # Shared dependencies (e.g. get_current_user)
├── models/             # SQLAlchemy ORM models (database tables)
├── schemas/            # Pydantic schemas (request/response validation)
├── services/           # Business logic (auth, job applications, notes)
├── utils/              # Helpers (e.g. pagination)
└── main.py             # Application entry point
```
 
 
Key design decisions:
 
- **Layered separation** — routers handle HTTP only and delegate to services; services contain business logic; models and schemas are kept distinct (ORM vs. validation).
- **Dependency injection** — database sessions and the current user are injected via FastAPI's `Depends`, which keeps the code composable and makes it easy to override dependencies in tests.
- **Ownership scoping** — all data-access queries filter by the authenticated user's id, protecting against IDOR (insecure direct object reference) vulnerabilities.
---
 
## Getting started
 
### Prerequisites
 
- Python 3.14
- PostgreSQL
### Installation
 
```bash
# 1. Clone the repository
git clone https://github.com/21jnco/job-tracker-api.git
cd job-tracker-api
 
# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
 
# 3. Install dependencies
pip install -r requirements.txt
```
 
 
### Configuration
 
Create a `.env` file in the project root:
 
```env
DATABASE_URL = os.getenv("DATABASE_URL")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
```
 
 
### Database setup
 
```bash
# Apply migrations to create the database schema
alembic upgrade head
```
 
### Running the app
 
```bash
uvicorn app.main:app --reload
```
 
The API will be available at `http://127.0.0.1:8000`.
Interactive documentation (Swagger UI) is at `http://127.0.0.1:8000/docs`.
 
---
 
## Running tests
 
The test suite uses pytest with a separate PostgreSQL test database (so tests never touch your development data).
 
```bash
# 1. Create a test database (once)
#    e.g. a database named "jobtracker_test"
 
# 2. Run the tests
python -m pytest
```
 
Test coverage includes:
 
- Security functions (password hashing, JWT creation/decoding, token expiry and tampering).
- Authentication endpoints (registration, login).
- Job application creation with authentication.
- Soft-delete behavior (a deleted application is no longer accessible).
 
---
 
## API overview
 
 
| Method | Endpoint                                      | Description                          | Auth |
|--------|-----------------------------------------------|--------------------------------------|------|
| POST   | `/auth/register`                              | Register a new user                  | No   |
| POST   | `/auth/login`                                 | Log in and receive a JWT token       | No   |
| GET    | `/job-applications`                           | List the current user's applications | Yes  |
| POST   | `/job-applications`                           | Create a job application             | Yes  |
| GET    | `/job-applications/{id}`                      | Get one application                  | Yes  |
| PATCH  | `/job-applications/{id}`                      | Update an application                | Yes  |
| DELETE | `/job-applications/{id}`                      | Soft-delete an application           | Yes  |
| PATCH  | `/job-applications/{id}/recovery`             | Restore a soft-deleted application   | Yes  |
| ...    | `/job-applications/{id}/notes`                | Notes CRUD (nested under application) | Yes  |
 
Full, always-up-to-date documentation is generated automatically at `/docs`.
 
---
 
## Roadmap / known limitations
 
- **Async** — the application is currently synchronous; migrating I/O-bound paths to async is a planned improvement.
- **Deployment** — containerization (Docker) and deployment are in progress.
- **Email reuse after account deletion** — currently a soft-deleted account keeps its email reserved; a configurable reuse strategy is a possible future enhancement.
