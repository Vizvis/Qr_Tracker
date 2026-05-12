# Qvoy Backend API — Project Context

## Overview
QR-based production tracking system. Physical items tracked via 8-digit QR tags through department-by-department scans. Supports QR lifecycle (register/activate/scan/release) and archival of completed production runs.

**Stack:** Python 3.11, FastAPI 0.104.1, PostgreSQL, SQLAlchemy 2.0.23 (async), Alembic 1.12.1, asyncpg 0.29.0, JWT/bcrypt auth

## Architecture
```
Route (core/routes/*.py)
  → Service (core/services/*.py)
    → DB Handler (db_handler/*.py)
      → SQLAlchemy async session
```

- Routes are thin — extract params, inject auth deps, call services, return responses
- Services contain all business logic and validation
- DB Handlers are repository-like data access objects (static async methods)
- DB engine is a singleton (`DatabaseManager` in `db_handler/database.py`)

## Folder Structure
```
Qr_Tracker/
├── main.py                     # FastAPI entry point, router mounting, CORS, exception handlers
├── config.py                   # Env config loader (DatabaseConfig, JWT settings, CORS)
├── auth/                       # Auth layer
│   ├── jwt_auth.py             # JWT create/verify, bcrypt hashing
│   ├── cookie_auth.py          # HTTP-only cookie handler + require_valid_auth_cookie()
│   └── dependencies.py         # RBAC: require_admin, require_supervisor, require_operator, require_viewer
├── core/
│   ├── routes/                 # FastAPI routers (6 files)
│   ├── services/               # Business logic (5 files)
│   └── pagination.py           # Page/page_size helpers, DEFAULT_PAGE_SIZE=10, MAX_PAGE_SIZE=50
├── db_handler/                 # DB access layer (6 files)
├── models/
│   ├── api_models/             # Pydantic request/response models
│   └── db_models/              # SQLAlchemy ORM models (7 tables)
├── alembic/                    # Migrations (33 versions)
├── scripts/                    # Utility scripts
├── requirements.txt
├── .env                        # Not committed
├── API_REFERENCE.md
├── DATABASE_SCHEMA.md
└── CLOUD_DB_SETUP.md
```

## Database (6 tables)
| Table | Purpose |
|---|---|
| `users` | Login accounts, UUID PK, role enum (viewer/operator/supervisor/admin) |
| `departments` | Production stations, ordered by sequence_order, active/inactive status |
| `qr_codes` | QR tags, 8-char string PK, lifecycle status tracking |
| `remarks` | In-progress scan data, unique on (qr_id, item_id, department_id) |
| `remarks_audit_log` | Immutable edit history for remarks (snapshot JSONB) |
| `produced_items` | Archived production records (read-only, denormalized) |

## Key Business Rules
- **Vertical cascade validation:** field_1..field_5 values can only decrease (not increase) as items move through departments
- **Edit lock:** non-admin users cannot edit a remark once the next department has scanned the same item
- **Item ID uniqueness:** an item_id can only be active on one QR at a time; checked against both `remarks` and `produced_items`
- **Session release:** copies all remarks → `produced_items`, deletes from `remarks`, resets QR to inactive
- **Audit logging:** every remark update creates a `remarks_audit_log` entry (immutable) and appends to `remarks_history` JSONB

## Auth
- JWT stored in HTTP-only cookies (`access_token` + `refresh_token`)
- bcrypt password hashing (passlib)
- Roles (ascending): viewer(1) < operator(2) < supervisor(3) < admin(4)
- Auth deps: `require_admin`, `require_supervisor` (admin+supervisor), `require_operator` (admin+supervisor+operator), `require_viewer` (any authenticated)

## Conventions
- All DB operations use async SQLAlchemy sessions (`AsyncSession`)
- Services receive `AsyncSession` and raise `HTTPException` for errors
- Pydantic models for API serialization in `models/api_models/`
- ORM models in `models/db_models/` with `Base` from `base.py`
- `.env` config loaded via `config.py` → `DatabaseConfig.get_database_url()`
- No tests configured; no linting/formatting tools set up

## Run Commands
```powershell
uvicorn main:app --reload          # Dev server at localhost:8000
alembic upgrade head               # Run migrations
pip install -r requirements.txt    # Install deps
```
