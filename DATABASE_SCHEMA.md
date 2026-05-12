# QR Tracker — Database Schema Reference

## Table Overview

| Table | Role |
|---|---|
| `users` | People who log in and perform actions |
| `departments` | Production stations a tag passes through |
| `qr_codes` | The physical QR tags |
| `remarks` | Live in-progress session data per tag/department |
| `remarks_audit_log` | Immutable edit history for every remark change |
| `produced_items` | Permanent archive of completed production sessions |

---

## `users`
**Who can log in and do things.**

Stores every person in the system. Each user has a **role** that controls what they're allowed to do. Accounts can be soft-deleted (deactivated) without erasing historical records.

| Column | Type | Description |
|---|---|---|
| `id` | UUID PK | Unique identifier |
| `name` | String | Display name |
| `phone_number` | String (unique) | Login identity |
| `email` | String (unique) | Login identity |
| `hashed_password` | String | bcrypt hash |
| `role` | Enum | `admin` / `supervisor` / `operator` / `viewer` |
| `is_active` | Boolean | `false` = deactivated account |
| `deactivated_at` | DateTime | When account was disabled |
| `created_at` | DateTime | Account creation timestamp |

---

## `departments`
**The production stations a tag travels through.**

Defines the departments in the factory (e.g. Production, QA, Packaging). `sequence_order` controls the order items physically flow through them. Departments can be deactivated without deleting historical data.

| Column | Type | Description |
|---|---|---|
| `id` | UUID PK | Unique identifier |
| `name` | String (unique) | Department name |
| `sequence_order` | Integer (unique) | Physical workflow order (1 → 2 → 3…) |
| `status` | Enum | `active` / `inactive` |
| `created_at` | DateTime | Creation timestamp |

---

## `qr_codes`
**The physical QR tags themselves.**

One row = one physical QR tag stuck on a product. Tracks the full lifecycle — who registered, activated, and deactivated it, and when it was last scanned.

| Column | Type | Description |
|---|---|---|
| `id` | String PK | 8-digit number printed on the physical tag |
| `status` | Enum | `active` (in use) / `inactive` (free) |
| `registered_by` | UUID FK → users | Admin who added the tag to the system |
| `enabled_by` | UUID FK → users | Supervisor who activated it for production |
| `enabled_at` | DateTime | When it was activated |
| `disabled_by` | UUID FK → users | Supervisor who released/closed it |
| `disabled_at` | DateTime | When it was released |
| `last_scanned_at` | DateTime | When an operator last scanned it |
| `notes` | String | Optional admin notes |
| `created_at` | DateTime | Tag registration timestamp |

> **Constraint:** `id` must match `^\d{8}$` — exactly 8 digits.

---

## `remarks`
**The live, in-progress session data for an active tag.**

This is the **working table**. When a tag is active and travelling through departments, every operator scan creates or updates a row here. Think of it as the tag's **current production session**.

| Column | Type | Description |
|---|---|---|
| `id` | UUID PK | Unique identifier |
| `qr_id` | String FK → qr_codes | Which QR tag this belongs to |
| `item_id` | String | What product/batch is on this tag |
| `department_id` | UUID FK → departments | Which department filled this row |
| `field_1` – `field_5` | Integer | Department-specific quantity counts |
| `issue_remarks` | String | Any problem noted by the operator |
| `custom_data` | JSONB | Flexible extra fields per department |
| `remarks_history` | JSONB | Inline edit log for this specific remark |
| `scanned_by` | UUID FK → users | Operator who first scanned in this dept |
| `last_edited_by` | UUID FK → users | Who last modified it |
| `scanned_at` | DateTime | When first scanned |
| `updated_at` | DateTime | Auto-updated on every edit |
| `created_at` | DateTime | Row creation timestamp |

> **Unique constraint:** One remark per `(qr_id + item_id + department_id)` — each department fills exactly one row per product session.

---

## `remarks_audit_log`
**The "who changed what and when" trail for remarks.**

Every time a remark row is edited, a full snapshot of the **old data** is saved here before the change is applied. This is a tamper-proof history — you can always see exactly what a remark looked like before any edit.

| Column | Type | Description |
|---|---|---|
| `id` | UUID PK | Unique identifier |
| `remark_id` | UUID FK → remarks (CASCADE) | Which remark was changed |
| `snapshot` | JSONB | Complete copy of the entire remark row at that moment |
| `changed_by` | UUID FK → users | Who made the edit |
| `changed_at` | DateTime | When the edit happened |

> Think of it like **version control for production data**. `remarks` always shows the current state; `remarks_audit_log` shows every past state. Rows are automatically deleted when the parent remark is deleted (CASCADE).

---

## `produced_items`
**The permanent archive of completed production sessions.**

When a supervisor **releases** a QR tag (closes the session), all remarks for that tag are copied into `produced_items` and the tag returns to `inactive`. This is a read-only historical record — the tag is free to be reused, but the production data lives here permanently.

| Column | Type | Description |
|---|---|---|
| `produced_id` | UUID PK | Unique identifier |
| `qr_id` | String | Which QR tag was used |
| `item_id` | String | Which product/batch was produced |
| `department_name` | String | Stored as text (not FK) so history is preserved if a dept is renamed |
| `field_1` – `field_5` | Integer | Final quantities from each department |
| `issue_remarks` | String | Any recorded issues |
| `scanned_by` | UUID FK → users | Operator who originally scanned |
| `last_edited_by` | UUID FK → users | Who last modified before archiving |
| `department_sequence` | Integer | Preserves dept order at time of archiving |
| `archived_at` | DateTime | When the tag was released |
| `created_at` | DateTime | Original creation timestamp |

---

## Entity Relationship Diagram

```
users ──────────────────────────────────────────────┐
  │                                                  │ FK: registered_by
  │ FK: scanned_by / last_edited_by                  ▼
  ├──────────────────────────► qr_codes ◄── (enabled_by, disabled_by)
  │                                │
  │                                │ FK: qr_id
  │                                ▼
departments ──── FK: department_id ──► remarks
                                        │
                                        ├──► remarks_audit_log  (every edit, CASCADE delete)
                                        │
                                        └──► produced_items     (on tag release/archive)
```

## Data Flow Summary

```
[Admin registers QR tag]
        │
        ▼
[Supervisor activates tag]  →  qr_codes.status = 'active'
        │
        ▼
[Operators scan at each dept]  →  remarks rows created/updated
        │                          remarks_audit_log rows on edits
        ▼
[Supervisor releases tag]  →  remarks → copied to produced_items
                               qr_codes.status = 'inactive'
                               remarks rows deleted
```
