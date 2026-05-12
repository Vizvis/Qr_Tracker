# QR Tracker — New Cloud Database Setup Guide

> Use this guide every time you onboard a new company or need to provision a fresh database for a new deployment.

---

## Prerequisites

Ensure the following are installed and accessible before starting:

| Tool | Purpose | Check |
|---|---|---|
| `psql` | PostgreSQL CLI for DB ops | `psql --version` |
| `pg_dump` / `pg_restore` | Backup & restore | `pg_dump --version` |
| Python 3.11+ | Running migrations | `python --version` |
| Alembic | Schema migration tool | `alembic --version` |
| GCP CLI (`gcloud`) | Managing Cloud SQL | `gcloud --version` |

---

## Step 1 — Create a GCP Cloud SQL Instance

1. Go to [GCP Console → Cloud SQL](https://console.cloud.google.com/sql)
2. Click **Create Instance** → choose **PostgreSQL**
3. Configure:
   - **Instance ID:** e.g. `qvoy-companyname`
   - **Password:** Set a strong password for the `postgres` user — **save it now**
   - **Region:** Choose closest to the company's location
   - **Database version:** PostgreSQL 15 (or latest stable)
   - **Machine type:** `db-f1-micro` is sufficient for small deployments
4. Under **Connections → Authorized networks**, add your current public IP:
   - Go to [whatismyip.com](https://www.whatismyip.com) to find your IP
   - Add it as: `YOUR.IP.HERE/32` with a label like `Dev Machine`
5. Click **Create** and wait for the instance to start (2–5 min)
6. Note the **Public IP** from the instance overview page

---

## Step 2 — Create the Application Database

Connect to the new Cloud SQL instance and create the database:

```powershell
# Replace <CLOUD_IP> with the public IP from Step 1
psql -h <CLOUD_IP> -U postgres -p 5432

# Inside psql:
CREATE DATABASE qvoycloud;
\q
```

---

## Step 3 — Update the `.env` File

Open `.env` in the `Qr_Tracker/` directory and fill in the new company's values:

```env
# Set to false to use Cloud DB
USE_LOCAL_DB=false

# GCP Cloud SQL credentials
DB_USER_CLOUD=postgres
DB_PASSWORD_CLOUD=<password you set in Step 1>
DB_HOST_CLOUD=<public IP from Step 1>
DB_PORT_CLOUD=5432
DB_NAME_CLOUD=qvoycloud

# SSL: always 'require' for GCP public IP
DB_SSL_MODE=require

# JWT — KEEP THIS THE SAME across restarts or all users get logged out
SECRET_KEY=<generate a random 64-char string — see note below>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS — set to the frontend URL for this company
CORS_ORIGINS=http://localhost:5173
```

> **Generating a SECRET_KEY:**
> ```powershell
> python -c "import secrets; print(secrets.token_urlsafe(48))"
> ```
> Copy the output into `SECRET_KEY`. Once set, **never change it** — changing it immediately invalidates all active sessions.

---

## Step 4 — Run Alembic Migrations (Apply Schema)

Alembic reads its database URL from `config.py`, which in turn reads from `.env`. Since you've already set `USE_LOCAL_DB=false` in Step 3, migrations will target the new Cloud DB automatically.

```powershell
# Navigate to the project directory
cd C:\Users\user\Documents\Code\Backend_Qvoy\Qr_Tracker

# Apply all migrations to the new database
alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Running upgrade -> abc123, initial schema
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, add session tables
...
```

If migrations succeed, the schema is fully set up. Verify:
```powershell
psql -h <CLOUD_IP> -U postgres -d qvoycloud -c "\dt"
```

---

## Step 5 — (Optional) Migrate Data from Another Database

Only follow this step if you need to copy data from an **existing** database (e.g., local dev or another company's instance).

### 5a — Dump the source database

```powershell
# Dump from local PostgreSQL
pg_dump -h localhost -U postgres -d QR_tracker -F c -f "C:\backup\qr_tracker_backup.dump"

# OR dump from an existing Cloud SQL instance
pg_dump -h <SOURCE_CLOUD_IP> -U postgres -d qvoycloud -F c -f "C:\backup\qr_tracker_backup.dump"
```

### 5b — Restore to the new Cloud DB

```powershell
pg_restore `
  -h <NEW_CLOUD_IP> `
  -U postgres `
  -d qvoycloud `
  --no-owner `
  --no-privileges `
  -v `
  "C:\backup\qr_tracker_backup.dump"
```

### 5c — Verify

```powershell
psql -h <NEW_CLOUD_IP> -U postgres -d qvoycloud -c "SELECT COUNT(*) FROM users;"
psql -h <NEW_CLOUD_IP> -U postgres -d qvoycloud -c "SELECT COUNT(*) FROM qr_codes;"
```

---

## Step 6 — Create the First Admin User

After migrations run, the database is empty. Create the first admin account via the API once the server is running (Step 7):

```powershell
# Register first admin (no auth required for first user if DB is empty,
# OR use psql to insert directly)

# Direct DB insert (safest for first admin):
psql -h <CLOUD_IP> -U postgres -d qvoycloud -c "
INSERT INTO users (id, name, phone_number, email, hashed_password, role, is_active, created_at)
VALUES (
  gen_random_uuid(),
  'Admin',
  '9999999999',
  'admin@company.com',
  '<bcrypt_hash>',
  'admin',
  true,
  NOW()
);
"
```

> **Generating a bcrypt hash for the password:**
> ```powershell
> python -c "from passlib.context import CryptContext; ctx = CryptContext(schemes=['bcrypt']); print(ctx.hash('YourPassword123'))"
> ```

After that, use `POST /api/users` from the API to add all subsequent users.

---

## Step 7 — Start the Backend Server

```powershell
cd C:\Users\user\Documents\Code\Backend_Qvoy\Qr_Tracker
uvicorn main:app --reload
```

Verify it connected successfully — you should see:
```
INFO:     Application startup complete.
```

If you see a connection error, jump to the [Troubleshooting](#troubleshooting) section.

---

## Step 8 — Whitelist the Production Server IP

If you are deploying the backend to a server (not running locally), you must whitelist that server's IP in GCP Cloud SQL too:

1. GCP Console → Cloud SQL → your instance → **Connections → Authorized Networks**
2. Add the production server's IP: `SERVER.IP.HERE/32`

> ⚠️ Never use `0.0.0.0/0` — this opens the DB to the entire internet.

---

## Quick Reference: Switching Between DBs

| Scenario | `.env` setting |
|---|---|
| Local development | `USE_LOCAL_DB=true` |
| Company A cloud DB | `USE_LOCAL_DB=false` + Company A credentials |
| Company B cloud DB | `USE_LOCAL_DB=false` + Company B credentials |

For each company, maintain a **separate `.env` file** and swap it in when needed. A good naming convention:
```
.env.local
.env.companyA
.env.companyB
```

Load a specific env file:
```powershell
# Temporarily point to a company-specific env
Copy-Item .env.companyA .env
uvicorn main:app --reload
```

---

## Checklist for Each New Company

- [ ] GCP Cloud SQL instance created and running
- [ ] Company's public IP (and dev machine IP) added to Authorized Networks
- [ ] `qvoycloud` database created on the instance
- [ ] `.env` updated with Cloud SQL credentials, `USE_LOCAL_DB=false`
- [ ] Fresh `SECRET_KEY` generated and saved
- [ ] `CORS_ORIGINS` set to the company's frontend URL
- [ ] `alembic upgrade head` run successfully
- [ ] First admin user created
- [ ] Server started and health check passes: `GET /api/health`
- [ ] Production server IP whitelisted (if not running locally)
- [ ] `.env` backed up securely (password manager / secrets vault — **never commit to git**)

---

## Troubleshooting

### `socket.gaierror: getaddrinfo failed`
The SSL parameter `?ssl=require` in the URL is not supported by asyncpg. This is already fixed in `db_handler/database.py` — SSL is passed via `connect_args`. If you see this error, ensure you're running the latest version of `database.py`.

### `Connection refused` / `TcpTestSucceeded: False`
```powershell
Test-NetConnection -ComputerName <CLOUD_IP> -Port 5432
```
If this fails, your IP is not whitelisted in GCP Authorized Networks. Add it (Step 1 → Authorized Networks).

### `password authentication failed`
Double-check `DB_PASSWORD_CLOUD` in `.env`. Passwords with special characters need no quoting in `.env` files, but avoid `#` (it starts a comment).

### `database "qvoycloud" does not exist`
Run Step 2 again — the database needs to be manually created before migrations.

### `alembic.util.exc.CommandError: Can't locate revision`
Your migration history is out of sync. Run:
```powershell
alembic history       # See existing revisions
alembic current       # See what the DB thinks its at
alembic upgrade head  # Re-apply missing migrations
```

### SSL Certificate Errors
The current setup uses `ssl.CERT_NONE` (no certificate verification) for simplicity with GCP Cloud SQL public IPs. If you need full certificate verification in future, replace in `database.py`:
```python
ssl_ctx.check_hostname = True
ssl_ctx.verify_mode = ssl.CERT_REQUIRED
ssl_ctx.load_verify_locations("path/to/server-ca.pem")
```
Download the server CA cert from GCP Console → Cloud SQL → your instance → **Connections → SSL**.

---

## File Reference

| File | Purpose |
|---|---|
| `.env` | All secrets and environment config — never commit |
| `config.py` | Reads `.env`, builds DB URL, exports settings |
| `db_handler/database.py` | Creates SQLAlchemy engine with SSL context |
| `alembic/` | Migration scripts — run `alembic upgrade head` |
| `alembic.ini` | Alembic config — `sqlalchemy.url` is overridden by `config.py` at runtime |
