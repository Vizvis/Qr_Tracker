# QR Tracker — API Reference

> **Base URL:** `http://<host>:8000`  
> **Interactive Docs:** `/api/docs` (Swagger UI) · `/api/redoc`  
> **Auth:** All protected endpoints require a valid `access_token` cookie set by `POST /api/users/login`.

---

## Role Hierarchy

| Role | Priority | Notes |
|---|---|---|
| `viewer` | 1 | Read-only access |
| `operator` | 2 | Can scan and post remarks |
| `supervisor` | 3 | Can enable/disable QR tags, view all |
| `admin` | 4 | Full access including user and tag management |

Roles are **hierarchical** — a higher role satisfies any lower-role requirement.

---

## 1. Users — `/api/users`

### `POST /api/users/login`
| | |
|---|---|
| **Auth** | None |
| **Body** | `{ email, password }` |
| **Returns** | `AuthResponse` — JWT token + user profile |
| **Service** | `UserService.login_user` |
| **DB Handler** | `UserDBHandler.get_by_email` → verifies bcrypt hash |
| **Side Effect** | Sets `access_token` HTTP-only cookie on the response |
| **Errors** | `401` invalid credentials · `403` account inactive |

---

### `POST /api/users/logout`
| | |
|---|---|
| **Auth** | Any logged-in user (cookie) |
| **Returns** | `{ message }` |
| **Service** | *(inline)* |
| **Side Effect** | Clears `access_token` cookie |

---

### `GET /api/users`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Query Params** | `page`, `page_size`, `roles` (repeatable or comma-separated) |
| **Returns** | Paginated `UserListResponse` |
| **Service** | `UserService.get_users` |
| **DB Handler** | `UserDBHandler.list_users_paginated` |

---

### `POST /api/users`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | `{ name, phone_number, email, password, role }` |
| **Returns** | `UserResponse` (201) |
| **Service** | `UserService.create_user` |
| **DB Handler** | `UserDBHandler.get_by_email` (dupe check) → `UserDBHandler.get_by_phone` (dupe check) → `UserDBHandler.create` |
| **Errors** | `409` email or phone already exists |

---

### `GET /api/users/me`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `UserResponse` for the currently authenticated user |
| **Service** | `UserService.get_user_by_id` |
| **DB Handler** | `UserDBHandler.get_by_id` |

---

### `PUT /api/users/me/password`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | `{ current_password, new_password }` |
| **Returns** | `{ message }` |
| **Service** | `UserService.change_password` |
| **DB Handler** | `UserDBHandler.get_by_id` → bcrypt verify → `UserDBHandler.update` |
| **Errors** | `400` wrong current password |

---

### `PUT /api/users/{user_id}/reset-password`
| | |
|---|---|
| **Auth** | Admin only |
| **Body** | `{ new_password }` |
| **Returns** | `{ message }` |
| **Service** | `UserService.admin_reset_password` |
| **DB Handler** | `UserDBHandler.get_by_id` → `UserDBHandler.update` |
| **Errors** | `403` non-admin attempt · `404` user not found |

---

### `GET /api/users/{user_id}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `UserResponse` |
| **Service** | `UserService.get_user_by_id` |
| **DB Handler** | `UserDBHandler.get_by_id` |

---

### `PUT /api/users/phone/{phone_number}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Path** | 10-digit phone number |
| **Body** | `UserUpdateRequest` (any subset of name, email, phone, password, role, is_active) |
| **Returns** | Updated `UserResponse` |
| **Service** | `UserService.update_user_by_phone` |
| **DB Handler** | `UserDBHandler.get_by_phone` → dupe checks → `UserDBHandler.update_by_phone` |
| **Side Effect** | Sets `deactivated_at` timestamp when `is_active=false` |

---

### `DELETE /api/users/phone/{phone_number}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `{ message }` |
| **Service** | `UserService.delete_user_by_phone` |
| **DB Handler** | `UserDBHandler.delete_by_phone` |

---

### `DELETE /api/users/{id}`
| | |
|---|---|
| **Auth** | Admin only |
| **Returns** | `{ detail }` |
| **Service** | `UserService.delete_user_by_id` |
| **DB Handler** | `UserDBHandler.delete` |
| **Errors** | `400` user has FK-linked records · `404` not found |

---

## 2. QR Codes — `/api/qr`

### `POST /api/qr`
| | |
|---|---|
| **Auth** | Admin |
| **Body** | `{ id (8-digit string), notes? }` |
| **Returns** | `QRCodeResponse` (201) |
| **Service** | `QRService.create_qr` |
| **DB Handler** | `QRDBHandler.get_by_id` (dupe check) → `QRDBHandler.create` |
| **Default State** | Created with `status = inactive` |
| **Errors** | `409` ID already exists |

---

### `GET /api/qr`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Query Params** | `page`, `page_size` |
| **Returns** | Paginated `QRCodeListResponse` |
| **Service** | `QRService.get_all_qrs_paginated` |
| **DB Handler** | `QRDBHandler.list_paginated` |

---

### `GET /api/qr/{id}`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Path** | 8-digit QR ID |
| **Returns** | `QRCodeResponse` |
| **Service** | `QRService.get_qr_by_id` |
| **DB Handler** | `QRDBHandler.get_by_id` |

---

### `PATCH /api/qr/{id}/enable`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Body** | `{ notes? }` |
| **Returns** | Updated `QRCodeResponse` |
| **Service** | `QRService.update_qr_status(id, "active", ...)` |
| **DB Handler** | `QRDBHandler.update_status` — sets `enabled_by`, `enabled_at` |

---

### `PATCH /api/qr/{id}/disable`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Body** | `{ notes? }` |
| **Returns** | Updated `QRCodeResponse` |
| **Service** | `QRService.update_qr_status(id, "inactive", ...)` |
| **DB Handler** | `QRDBHandler.update_status` — sets `disabled_by`, `disabled_at` |

---

### `PUT /api/qr/{id}/status`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Body** | `{ status: "active" \| "inactive", notes? }` |
| **Returns** | `{ detail }` |
| **Service** | `QRService.update_qr_status` |
| **Notes** | Generic combined status toggle via PUT |

---

### `POST /api/qr/enable`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Body** | `{ user_id, qr_code_id, notes? }` |
| **Returns** | `QRCodeResponse` |
| **Service** | `QRService.enable_qr_from_input` |
| **Validation** | `user_id` in body must match authenticated user |

---

### `POST /api/qr/disable`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Body** | `{ user_id, qr_code_id, notes? }` |
| **Returns** | `QRCodeResponse` |
| **Service** | `QRService.disable_qr_from_input` |
| **Validation** | `user_id` in body must match authenticated user |

---

### `DELETE /api/qr/{id}`
| | |
|---|---|
| **Auth** | Admin |
| **Notes** | No 8-digit format enforcement — allows cleanup of malformed tags |
| **Returns** | `{ detail }` |
| **Service** | `QRService.delete_qr` |
| **DB Handler** | `QRDBHandler.delete_qr` |

---

## 3. Session — `/api/session`

> Sessions represent the active lifecycle of a QR tag between activation and release. Each active QR accumulates department remarks until it is released/archived.

### `GET /api/session/active-qrs`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Query Params** | `page`, `page_size` |
| **Returns** | Paginated list of active QR tags with all their current remarks |
| **Service** | `SessionService.get_active_qrs_with_remarks` |
| **DB Handler** | `SessionDBHandler.list_active_qr_remarks` |

---

### `GET /api/session/{qr_id}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `{ qr_id, remarks[] }` in ascending `created_at` order |
| **Service** | `SessionService.get_session` |
| **DB Handler** | `QRDBHandler.get_by_id` → `SessionDBHandler.list_remarks_by_qr_id` |
| **Notes** | Returns empty remarks list if QR is inactive |

---

### `GET /api/session/{qr_id}/previous-state`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `{ qr_id, final_state }` — only the **latest** remark row |
| **Service** | `SessionService.get_previous_state` |
| **DB Handler** | `SessionDBHandler.get_latest_remark_by_qr_id` |

---

### `POST /api/session/{qr_id}/remarks`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | `{ item_id, department_id, field_1..5, issue_remarks?, custom_data? }` |
| **Returns** | Created remark (201) |
| **Service** | `SessionService.create_session_remark` → `SessionService.create_remark` |
| **DB Handler** | `QRDBHandler.get_by_id` · `DepartmentDBHandler.get_by_id` · `SessionDBHandler.has_department_update` · `SessionDBHandler.create_remark` |
| **Validations** | QR must be active · Department must be active · No duplicate dept per session · No duplicate item+dept per session · item_id not in use on another QR · Field values must not exceed previous department's values (cascade rule) |
| **Errors** | `400` QR/dept inactive · `409` duplicate remark |

---

### `PUT /api/session/{qr_id}/remarks/{remark_id}`
### `PATCH /api/session/{qr_id}/remarks/{remark_id}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | `{ field_1..5?, issue_remarks? }` |
| **Returns** | Updated remark |
| **Service** | `SessionService.update_session_remark` |
| **DB Handler** | `SessionDBHandler.get_by_id` → `SessionDBHandler.update_remark` |
| **Edit Lock** | Non-admins cannot edit once a **subsequent** department has already scanned the same item |
| **Validations** | Same cascade validation as create |
| **Errors** | `403` edit locked · `404` remark not found |

---

### `PATCH /api/session/{qr_id}/close`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `{ qr_id, archived_count, message }` |
| **Service** | `SessionService.release_session` |
| **DB Handler** | `QRDBHandler.get_by_id` → `SessionDBHandler.release_session` |
| **Side Effects** | Copies all session remarks into `produced_items` archive table · Clears remarks from `remarks` table · Sets QR tag status → `inactive` |
| **Errors** | `400` QR not active |

---

## 4. Remarks — `/api/remarks`

> Lower-level direct remarks API (no `qr_id` in path). Mostly used internally or for admin overrides.

### `GET /api/remarks`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Query Params** | `page`, `page_size` |
| **Returns** | Paginated list of all current remarks |
| **Service** | `SessionService.get_remarks` |
| **DB Handler** | `SessionDBHandler.list_all_remarks` |

---

### `POST /api/remarks`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | `{ qr_id, item_id, department_id, field_1..5, issue_remarks?, custom_data? }` |
| **Returns** | Created remark (201) |
| **Service** | `SessionService.create_remark` |
| **Notes** | Same validations as `POST /api/session/{qr_id}/remarks` |

---

### `PATCH /api/remarks/{remark_id}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | Any subset of `{ item_id, department_id, field_1..5, issue_remarks, custom_data }` |
| **Returns** | Updated remark |
| **Service** | `SessionService.update_remark` |
| **DB Handler** | `SessionDBHandler.get_by_id` → `SessionDBHandler.update_remark` |
| **Notes** | No edit-lock check here (unlike session route) · `department_id` change triggers dupe check |

---

## 5. Departments — `/api/departments`

### `GET /api/departments`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Query Params** | `page`, `page_size` |
| **Returns** | Paginated `DepartmentListResponse` |
| **Service** | `DepartmentService.get_departments` |
| **DB Handler** | `DepartmentDBHandler.list_paginated` |

---

### `POST /api/departments`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | `{ name, sequence_order, status? }` |
| **Returns** | `DepartmentResponse` (201) |
| **Service** | `DepartmentService.create_department` |
| **DB Handler** | `DepartmentDBHandler.create` |

---

### `PUT /api/departments/{department_id}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Body** | `{ name?, sequence_order?, status? }` |
| **Returns** | Updated `DepartmentResponse` |
| **Service** | `DepartmentService.update_department` |
| **DB Handler** | `DepartmentDBHandler.update` |

---

### `DELETE /api/departments/{department_id}`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | 204 No Content |
| **Service** | `DepartmentService.delete_department` |
| **DB Handler** | `DepartmentDBHandler.delete` |

---

## 6. Produced Items — `/api/produced-items`

> Read-only archive of completed production runs. Records are written here automatically when a QR session is released (`PATCH /api/session/{qr_id}/close`).

### `GET /api/produced-items`
| | |
|---|---|
| **Auth** | Admin |
| **Query Params** | `page`, `limit`, `search` (qr_id / item_id / remarks), `start_date`, `end_date` |
| **Returns** | Paginated `ProductionHistoryPaginatedResponse` |
| **Service** | `ProducedItemsService.search_production_history` |
| **DB Handler** | `ProducedItemsDBHandler.search_paginated` |

---

### `GET /api/produced-items/qr/{qr_id}`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Query Params** | `page`, `page_size` |
| **Returns** | Paginated `ProducedItemsPaginatedResponse` grouped by item_id |
| **Service** | `ProducedItemsService.get_by_qr_id_paginated` |
| **DB Handler** | `ProducedItemsDBHandler.get_by_qr_id` |

---

### `GET /api/produced-items/item/{item_id}`
| | |
|---|---|
| **Auth** | Supervisor+ |
| **Query Params** | `page`, `page_size` |
| **Returns** | Paginated `ProducedItemsPaginatedResponse` |
| **Service** | `ProducedItemsService.get_by_item_id_paginated` |
| **DB Handler** | `ProducedItemsDBHandler.get_by_item_id` |

---

## 7. Health & Root

### `GET /api/health`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `{ status: "healthy", message, service }` |

### `GET /`
| | |
|---|---|
| **Auth** | Any logged-in user |
| **Returns** | `{ message, docs, redoc, health }` |

---

## Error Response Format

All errors return a consistent JSON body:

```json
{
  "error_type": "HTTPException",
  "detail": "Human-readable error message",
  "path": "/api/users/login",
  "timestamp": "2026-05-12T08:00:00Z",
  "trace": null
}
```

> `trace` is only populated when `DEBUG=true` in `.env`.

---

## Request Flow Diagram

```
HTTP Request
    │
    ▼
CORSMiddleware (allowed origins from CORS_ORIGINS env var)
    │
    ▼
Route Handler (core/routes/*.py)
    │
    ├── Auth Dependency (auth/dependencies.py)
    │       └── CookieAuth → JWTAuth.verify_token
    │
    ▼
Service Layer (core/services/*.py)
    │   Business logic, validation, error handling
    │
    ▼
DB Handler (db_handler/*_db_handler.py)
    │   SQLAlchemy async queries
    │
    ▼
PostgreSQL (local or GCP Cloud SQL)
```
