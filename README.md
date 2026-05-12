# Qvoy — Backend API

Production QR tracking system built with FastAPI and PostgreSQL. Tracks items through department-by-department production scans, manages QR tag lifecycles, and archives completed production runs.

---

## Tech Stack

| Layer      | Technology                                  |
| ---------- | ------------------------------------------- |
| API        | FastAPI (Python 3.11+)                      |
| Database   | PostgreSQL — local or GCP Cloud SQL         |
| ORM        | SQLAlchemy (async)                          |
| Migrations | Alembic                                     |
| Auth       | JWT via HTTP-only cookie (passlib + bcrypt) |

---

## Getting Started

### 1. Install dependencies

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root. The minimum required fields:

```env
# Database — set to true for local PostgreSQL, false for GCP Cloud SQL
USE_LOCAL_DB=true

# Local DB
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=QR_tracker

# Cloud DB (GCP Cloud SQL) — only needed when USE_LOCAL_DB=false
DB_USER_CLOUD=postgres
DB_PASSWORD_CLOUD=yourpassword
DB_HOST_CLOUD=<cloud-sql-public-ip>
DB_PORT_CLOUD=5432
DB_NAME_CLOUD=qvoycloud
DB_SSL_MODE=require

# JWT — generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS — set to your frontend URL
CORS_ORIGINS=http://localhost:5173
```

### 3. Run migrations

```powershell
alembic upgrade head
```

### 4. Start the server

```powershell
uvicorn main:app --reload
```

API is available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/api/docs`

---

## Authentication

All endpoints (except `POST /api/users/login`) require a valid session cookie. Login returns a JWT stored as an HTTP-only cookie — no manual token handling needed in the frontend.

**Roles** (in ascending order of privilege): `viewer` → `operator` → `supervisor` → `admin`

---

## Key Workflows

**Activate a tag** → `POST /api/qr/enable` (Supervisor+)  
**Operator scans** → `POST /api/session/{qr_id}/remarks`  
**Release tag** → `PATCH /api/session/{qr_id}/close` — archives all scan data to `produced_items` and resets the tag to inactive  
**View history** → `GET /api/produced-items` (Admin)

See [`API_REFERENCE.md`](./API_REFERENCE.md) for full endpoint documentation.

---
