# Backend Merge Summary & Frontend AI Guide

**Context for the Frontend AI Agent:**
The backend repository (`Qr_Tracker`) has just undergone a major merge on the `Sivanath-test` branch. Merge conflicts were resolved by **retaining both incoming remote changes and recent local feature additions**. This document outlines the available API methods, payload structures, and state changes so the frontend can flawlessly integrate with the new backend capabilities.

---

## 1. State & Database Adjustments
*   **No more `pending` status**: The `qr_status` ENUM has been updated in the Postgres database. The only valid states for a QR Code are now `"active"` and `"inactive"`.
*   **Strict 8-Digit Physical Tags**: The database and the `FastAPI` path parameters enforce a strict exactly-8-digits constraint (`^\d{8}$`) on QR Code IDs, except for the Admin `DELETE` route (which allows cleanup of legacy broken scans).
*   **User Roles**: Now serialized as strict integers (`1` = operator, `2` = supervisor, `3` = admin) when returned to the frontend.

---

## 2. Updated QR Code API Routes

The backend now supports two different styles for toggling QR codes, owing to the merge combinations. The frontend can use whichever perfectly fits the UI payload data available.

### Toggle QR via ID (RESTful PUT)
*   **`PUT /api/qr/{id}/status`**
*   **Path Param `id`**: Must be exactly 8 digits.
*   **Payload**: `QRTagStatusUpdate` => `{ "status": "active" | "inactive" }`
*   **Auth**: Supervisor+

### Toggle QR via Payload (Explicit POST from Remote)
*   **`POST /api/qr/enable`**
*   **`POST /api/qr/disable`**
*   **Payload**: `QRCodeToggleRequest` => `{ "user_id": "uuid", "qr_code_id": "string", "notes": "string" }`
*   **Auth**: Supervisor+
*   **Notes**: Must pass the current `user_id`, which the backend strictly matches against the authenticated token.

### Administrative Deletion
*   **`DELETE /api/qr/{id}`**
*   **Path Param `id`**: Any string (bypass 8-digit constraint to delete legacy test tags).
*   **Auth**: Admin only
*   **Behavior**: Cascades and deletes associated `remarks` and `produced_items`.

### End Session (Work-In-Progress)
*   **`POST /api/qr/{id}/finish-session`**
*   **Path Param `id`**: Must be exactly 8 digits.
*   **Behavior**: Takes all active logs in the `remarks` table for this QR, moves them to the permanent `produced_items` table, and wipes the temporary `remarks`. Converts QR status to inactive (to be confirmed by logic, but handled by service naturally).

---

## 3. Updated User API Routes

### User Retrieval
*   **`GET /api/users`**
*   **Response**: Now perfectly wrapped in a `UserListResponse` which handles pagination metadata alongside the `UserResponse` array.

### Password Management (Added locally)
*(Note: These routes may be nested under `/api/users`)*
*   **Change Own Password**: `PUT` route for standard users requiring `current_password` and `new_password` (via `ChangePasswordRequest`).
*   **Admin Reset Password**: `PUT` route for Admins requiring only `new_password` against a target `user_id` (via `AdminPasswordResetRequest`).

---

## 4. Frontend Implementation Guidelines
1.  **Status Badges**: If you were checking for `status === 'pending'`, remove that check. Map statuses directly to `active` (e.g., green/blue) and `inactive` (e.g., gray).
2.  **QR ID Input Validations**: Add client-side regex checking (`^\d{8}$`) to any text field searching for, activating, or working on a QR Code so an invalid request is prevented before hitting the backend.
3.  **Active Session Timeline**: When mapping timelines via `GET /api/session/active-qrs`, remember that the `remarks` array is nested directly inside the QR object in the JSON response, meaning no secondary fetch is needed for timeline rendering. Display this context in a horizontally scrollable div rather than flex-wrap to keep dashboard card heights consistent.
