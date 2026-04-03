# Qvoy Database Schema Documentation

## 1. TABLE INVENTORY

| Table Name | Purpose | Defined In |
|---|---|---|
| `department` | Represents a department/stage in the manufacturing process (Production, Quality, etc.). Defines the sequence order for the UI. | `models/db_models/department.py` |
| `produced_items` | Links a scanned item (represented by `item_id`) to a physical QR tag (`qr_id`) within a department. Stores the initial scanning information. | `models/db_models/produced_items.py` |
| `qr_codes` | Represents the physical QR tags in the facility. Tracks their lifecycle status (`active`, `inactive`) and the timeline/users who enabled or disabled them. | `models/db_models/qr_code.py` |
| `remarks` | Stores the actual inspection details, general notes, and issues logged against an item and its QR tag inside a specific department. | `models/db_models/remarks.py` |
| `users` | Contains user authentication info, contact details, and their granular application role mapping (Admin, Operator, etc.). | `models/db_models/user.py` |

---

## 2. FULL COLUMN DETAILS

### Table: `department`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid4 | Unique identifier for the department. |
| `name` | VARCHAR(255) | NOT NULL, UNIQUE | The name of the department (e.g., "Quality Assurance"). |
| `sequence_order` | INTEGER | NOT NULL, UNIQUE | Numeric order to dictate flow/UI presentation of departments. |
| `status` | ENUM | NOT NULL, DEFAULT 'active' | Tracks if the department is currently in operation (`active` or `inactive`). |
| `head_of_department` | UUID | FK (users.id), NULL | A reference to the User ID who leads this department. |
| `created_on` | TIMESTAMP | DEFAULT utcnow() | Date and time the department was created. |

### Table: `produced_items`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `produced_id` | UUID | PRIMARY KEY, DEFAULT uuid4 | Unique identifier for a scanned production log. |
| `qr_id` | VARCHAR | FK (qr_codes.id), NOT NULL | The ID of the physical QR tag tracking this item. |
| `item_id` | VARCHAR | NOT NULL | The specific manufacturing ID or SN of the item being tracked. |
| `department_id` | UUID | FK (department.id), NOT NULL | The department where this scan took place. |
| `general_remarks` | VARCHAR | NULL | Optional text for general observations during the scan. |
| `issue_remarks` | VARCHAR | NULL | Optional text for reporting issues or defects during the scan. |
| `created_by` | UUID | FK (users.id), NULL | User ID of the operator doing the initial scan. |
| `updated_by` | UUID | FK (users.id), NULL | User ID modifying the initial scan metrics. |
| `remark_by` | UUID | FK (users.id), NULL | User ID attaching the initial remarks. *(Note: Redundant with `remarks` table).* |
| `remark_updated` | UUID | FK (users.id), NULL | User ID updating the initial remarks. *(Note: Redundant with `remarks` table).* |
| `created_at` | TIMESTAMP | DEFAULT utcnow(), NOT NULL | Time the item scan was logged. |

### Table: `qr_codes`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR | PRIMARY KEY, CHECK format | Unique ID scanned from the physical tag (must be an 8-digit numeric string). |
| `status` | ENUM | NOT NULL, DEFAULT 'inactive' | Current state of the QR tag (`active`, `inactive`). |
| `registered_by` | UUID | FK (users.id), NOT NULL | User ID who first introduced this tag into the system. |
| `enabled_by` | UUID | FK (users.id), NULL | User ID who last marked this tag as `active`. |
| `enabled_at` | TIMESTAMP | NULL | When the tag was last marked active. |
| `disabled_by` | UUID | FK (users.id), NULL | User ID who last marked this tag as `inactive` or released it. |
| `disabled_at` | TIMESTAMP | NULL | When the tag was last deactivated. |
| `created_at` | TIMESTAMP | DEFAULT utcnow(), NOT NULL| Time the tag was registered. |
| `notes` | VARCHAR | NULL | General notes concerning the tag. |

### Table: `remarks`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid4 | Unique identifier for a remark log. |
| `qr_id` | VARCHAR | FK (qr_codes.id), NULL | The QR session this remark belongs to. |
| `item_id` | VARCHAR | NOT NULL | The manufactured item being remarked on. *(See Indexes section for constraint details)* |
| `department_id` | UUID | FK (department.id), NULL | The department logging the remark. |
| `general_remarks` | VARCHAR | NULL | General notes logged by the operator. |
| `issue_remarks` | VARCHAR | NULL | Defect/issue notes logged. |
| `remarks_history` | JSONB | NOT NULL, DEFAULT '[]' | JSON array containing a timeline of previous edits/revisions to these remarks. |
| `remark_by` | UUID | FK (users.id), NULL | User ID who created the remark. |
| `remark_updated` | UUID | FK (users.id), NULL | User ID who last edited the remark. |
| `created_at` | TIMESTAMP | DEFAULT utcnow(), NOT NULL | Timestamp when the remark was created. |
| `updated_at` | TIMESTAMP | DEFAULT utcnow() on update | Automatic timestamp updated upon row edit. |

### Table: `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT uuid4 | Unique identifier for a user account. |
| `name` | VARCHAR | NOT NULL | Personal name of the user. |
| `phone_number` | VARCHAR | NOT NULL, UNIQUE | Phone number for contact. |
| `email` | VARCHAR | NOT NULL, UNIQUE | Email address for login and contact. |
| `hashed_password` | VARCHAR | NOT NULL | Bcrypt-hashed password. |
| `role` | ENUM | NOT NULL | App privilege level (Admin, Supervisor, etc.). |
| `is_active` | BOOLEAN | DEFAULT true | True if the user account is open and able to log in. |
| `created_at` | TIMESTAMP | DEFAULT utcnow() | Date the user was imported. |

---

## 3. RELATIONSHIPS & FOREIGN KEYS

1. **`department.head_of_department` → `users.id`** (One-to-One / One-to-Many):
   - A Department can have designated a single head User. A user could theoretically head multiple departments.
2. **`produced_items.qr_id` → `qr_codes.id`** (Many-to-One):
   - A scanned item is tied to a specific tag. One QR tag can be reused across hundreds of items over time.
3. **`produced_items.department_id` → `department.id`** (Many-to-One):
   - A scan takes place inside exactly one department. A department handles thousands of scans.
4. **`produced_items.created_by` / `updated_by` / `...` → `users.id`** (Many-to-One):
   - Establishes the operator identity performing the scan processing action.
5. **`qr_codes.registered_by` / `enabled_by` / `disabled_by` → `users.id`** (Many-to-One):
   - Tracks which administrative users controlled the hardware lifecycle of the QR tag.
6. **`remarks.qr_id` → `qr_codes.id`** (Many-to-One):
   - Maps the inspection remarks directly to the active session tag.
7. **`remarks.department_id` → `department.id`** (Many-to-One):
   - The department the remarks apply to.
8. **`remarks.remark_by` / `remark_updated` → `users.id`** (Many-to-One):
   - Logs which operator recorded or revised the inspection.

---

## 4. ENUMS & CUSTOM TYPES

| Enum/Type Name | Possible Values | Table & Column |
|---|---|---|
| `departmentstatus` | `active`, `inactive` | `department.status` |
| `RoleLevel` | `admin`, `supervisor`, `operator`, `viewer` | `users.role` |
| `qr_status_enum` | `active`, `inactive` | `qr_codes.status` |

---

## 5. INDEXES

Outside of Primary/Foreign Keys, the database relies on:

1. **`department` table:**
   - **`name` (UNIQUE)**: Prevents two departments from having the identical name.
   - **`sequence_order` (UNIQUE)**: Enforces a strict pipeline order (e.g. no two departments can be flow "Step 1").
2. **`users` table:**
   - **`phone_number` (UNIQUE)**: Login/Identity verification index.
   - **`email` (UNIQUE)**: Standard authentication unique restriction.
3. **`remarks` table:**
   - **`uq_remarks_qr_item_department` (UNIQUE Composite)**: Ensures that for a given tag (`qr_id`), for a given item (`item_id`), and a given department (`department_id`), there can only be **one** active remarks row.
   - **`item_id` (UNIQUE)**: Due to a recent Alembic migration (`b98a46e91684_make_item_id_unique_in_remarks.py`), the `item_id` alone is strictly unique in the remarks table. *(Note: This might conflict with the intended flow if an item goes to multiple departments!)*
4. **`qr_codes` table:**
   - **`ck_qr_code_id_format` (CHECK CONSTRAINT)**: Ensures the primary key string is exactly 8 numeric digits.

---

## 6. MISSING TABLES (GAP ANALYSIS)

While evaluating the core requirements of Qvoy, these additions or modifications should be made:

1. **Missing Table: `tag_sessions` (or fixing the dual nature of `produced_items`)**
   - **Why:** The system currently relies on the state of `qr_codes.status = active` to determine if a tag is tracking an item, and loosely binds `produced_items` and `remarks` directly to the `qr_id`. If a tag completes its journey and is reused, querying `SELECT * FROM remarks WHERE qr_id = X` will return historical data from *previous manufacturing cycles*.
   - **Fix:** Introduce a `tag_sessions` table (`id`, `qr_id`, `item_id`, `started_at`, `completed_at`). The `remarks` and `produced_items` should point to `session_id`, not `qr_id`, guaranteeing logical separation between cycles.

2. **Missing Feature: "Custom Fields Per Scan"**
   - **Why:** Your requirements request "Per-department custom fields per scan". Currently, the schema hardcodes exactly two columns: `general_remarks` and `issue_remarks`. If the Packaging department needs "Weight (kg)" and Quality needs "Defect Type Enum", the schema cannot support it.
   - **Fix:** Add a JSONB column `custom_fields` to `remarks` OR create a `department_form_schema` table to define what inputs each department requires during a scan.

3. **Data Quality Issue: The `item_id` Unique Constraint on `remarks`**
   - **Why:** Migration `b98a46e9` aggressively enforced a UNIQUE constraint directly on `remarks.item_id`. This means if Item "123" visits the Production department and gets a remark, it can *never* receive a remark in the Quality department, because the DB will reject the row as a duplicate `item_id`. This effectively destroys multi-department tracking.

---

## 7. ORM SETUP

- **Library:** SQLAlchemy 2.0 (using `declarative_base()`).
- **Async Execution:** Utilizes SQLAlchemy's Async engine (`create_async_engine`, `AsyncSession`) with `asyncpg` driver.
- **Base Class:** All models inherit from `models.db_models.base.Base`.
- **Database:** PostgreSQL. Demonstrated by the usage of strict Postgres dialects like `sqlalchemy.dialects.postgresql.UUID` and `JSONB`.
- **Migrations:** Managed completely by Alembic. The migration history is actively managed under the `alembic/versions` directory.

---

## 8. SCHEMA DIAGRAM (TEXT FORMAT)

```text
users
  └── id (PK)
  └── name
  └── phone_number
  └── email
  └── hashed_password
  └── role
  └── is_active
  └── created_at

department
  └── id (PK)
  └── name
  └── sequence_order
  └── status
  └── head_of_department (FK → users.id)
  └── created_on

qr_codes
  └── id (PK)
  └── status
  └── registered_by (FK → users.id)
  └── enabled_by (FK → users.id)
  └── disabled_by (FK → users.id)
  └── notes
  └── timestamps...

produced_items
  └── produced_id (PK)
  └── qr_id (FK → qr_codes.id)
  └── item_id 
  └── department_id (FK → department.id)
  └── general_remarks
  └── issue_remarks
  └── timestamps / users ...

remarks
  └── id (PK)
  └── qr_id (FK → qr_codes.id)
  └── item_id
  └── department_id (FK → department.id)
  └── general_remarks
  └── issue_remarks
  └── remarks_history
  └── timestamps / users ...


Relationships:
users ──────< department        (One user heads many departments)
users ──────< qr_codes          (One user manages many tags)
users ──────< produced_items    (One user logs many items)
users ──────< remarks           (One user writes many remarks)

qr_codes ───< produced_items    (One tag logs many item scans)
qr_codes ───< remarks           (One tag hosts many remarks)

department ─< produced_items    (One dept hosts many item scans)
department ─< remarks           (One dept hosts many remarks)
```