# Afinpe API (Django + DRF)

**Features**

- PostgreSQL (via env vars)
- JWT Auth (SimpleJWT)
- Public signup + Admin-only user creation
- Role distinction (admin vs common user)
- CRUD for all entities mirroring the provided SQLite schema
- Filtering (`django-filter`), pagination, ordering
- API versioning via URL (`/api/v1/...`)
- OpenAPI docs with **drf-spectacular** (Swagger & Redoc)
- CORS
- Dockerfile + docker-compose for production-like run
- Structured logs

## Quickstart (Local)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Make your .env from the example
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Docs at:

- Swagger UI: http://localhost:8000/api/v1/schema/swagger-ui/
- Redoc: http://localhost:8000/api/v1/schema/redoc/

JWT:

- Obtain: `POST /api/v1/auth/jwt/create/` (with username & password)
- Refresh: `POST /api/v1/auth/jwt/refresh/`

Signup:

- Public: `POST /api/v1/auth/signup/` (creates a common user)
- Admin create user: `POST /api/v1/auth/admin/create-user/` (admin-only)

## Docker

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Environment

See `.env.example` for required variables.
