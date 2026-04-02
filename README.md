# QR Tracker

A FastAPI-based QR code tracking system for production process monitoring.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase cloud or local)
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **Auth**: JWT (python-jose + passlib)
- **QR Generation**: qrcode library

## Project Structure

```
├── app/
│   ├── core/
│   │   ├── config.py           # Database & environment config
│   │   ├── database.py         # Database engine setup
│   │   └── __init__.py
│   ├── models/
│   │   ├── base.py             # Base model
│   │   ├── enums.py            # Enums (RoleLevel, DepartmentEnum)
│   │   ├── user.py             # User model
│   │   ├── qr_code.py          # QR Code model
│   │   ├── department.py       # Department model
│   │   ├── production_session.py
│   │   ├── scan_event.py
│   │   ├── produced_items.py
│   │   └── __init__.py
│   └── __init__.py
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   ├── env.py                  # Migration environment config
│   └── script.py.mako          # Migration template
├── requirements.txt            # Python dependencies
├── alembic.ini                # Alembic configuration
├── .env.example               # Example environment variables
└── README.md

```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

**For Cloud (Default)**:

- Set `USE_LOCAL_DB=False`
- Add your Supabase credentials (URL, password, etc.)

**For Local Development**:

- Set `USE_LOCAL_DB=True`
- Ensure PostgreSQL is running locally

### 4. Run Migrations

Create initial migration:

```bash
alembic revision --autogenerate -m "Initial migration"
```

Apply migrations:

```bash
alembic upgrade head
```

## Database Models

### Models Included:

- **User**: Users with roles (admin, supervisor, operator, viewer)
- **QRCode**: QR code tracking with status (pending, active, inactive)
- **Department**: Departments with types (production, QA, packaging, etc.)
- **ProductionSession**: Production batches tracked via QR codes
- **ScanEvent**: Track scanning events across departments
- **ProducedItems**: Final produced items with approvals

## Environment Configuration

Switch between cloud and local databases by modifying `.env`:

```env
# For Cloud Supabase
USE_LOCAL_DB=False

# For Local PostgreSQL
USE_LOCAL_DB=True
```

No code changes needed - the config handles both automatically!

## Getting Started

1. Set up venv and install dependencies (steps 1-2 above)
2. Configure `.env` file with credentials
3. Run migrations: `alembic upgrade head`
4. Start building your FastAPI endpoints!
