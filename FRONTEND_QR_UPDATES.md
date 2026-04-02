# Frontend Required Changes: QR Deletion & Status Updates

Based on the recent backend updates, the frontend needs to be adjusted to support the new database constraints and endpoints.

## 1. QR Tag Status Enum Changes

- **Problem Fixed**: QR codes were defaulting to `pending`, which added unnecessary complexity to the status flow.
- **Change**: The `pending` status has been **completely removed** from the database ENUM.
- **Action**:
  - The frontend should no longer expect, display, or send `"pending"` as a status.
  - The only valid statuses moving forward are **`"active"`** and **`"inactive"`**.
  - Newly registered QR tags now permanently default to `"inactive"` upon creation.

## 2. Permanent QR Tag Deletion

- **Endpoint**: `DELETE /api/qr/{id}`
- **Permissions**: **Strictly Admin Only (Role 3)**
- **Behavior**: Permanently deletes a physical QR tag from the system by its string ID. It also recursively deletes all associated `Remarks` and `ProducedItems` linked to that tag (cascade delete).
- **Action**: Add a "Delete Tag" button in the Admin-facing Registered QR Tags view.
- **Validation Note**: Unlike the GET/POST endpoints, this DELETE endpoint **deliberately bypasses the 8-digit exact regex validation** (`^\d{8}$`). This allows administrators to use the frontend UI to delete broken legacy tags or accidental string scans (like `www.google.com`) that got trapped in the database earlier.
- **Expected Responses**:
  - `200 OK`: `{"detail": "QR tag deleted successfully"}`
  - `404 Not Found`: `{"detail": "Tag ID not found"}`
  - `403 Forbidden`: `{"detail": "Not authorized. Admin access required."}`
