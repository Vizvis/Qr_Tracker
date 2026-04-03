# Pagination Guide for Frontend Integration

This document outlines how pagination works across the Qvoy backend API to ensure seamless integration with the frontend UI (tables, lists, endless scrolling).

## Overview
The Qvoy backend uses standard **Offset-Based Pagination**. Most endpoints that return a list of items (`GET /api/departments`, `GET /api/remarks`, `GET /api/session/active-qrs`, etc.) support pagination.

---

## Request Parameters

When fetching a paginated list, you can pass two query parameters in the URL:

| Parameter | Type | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `page` | `integer` | `1` | Minimum: `1` | The current page number you want to retrieve. |
| `page_size` | `integer` | `10` | Minimum: `1`, Maximum: `10` | The number of items to return per page. Max capped internally. |

> **Note:** The backend strictly enforces a maximum `page_size` of **10**. If you send `?page_size=50`, the server will safely normalize it down to `10` or return a validation error (depending on route strictness) to prevent database overload.

### Example Request
```http
GET /api/departments?page=2&page_size=5
```

---

## Response Structure

All paginated endpoints return a standard JSON structure. This allows the frontend to use a single generic interface/type to handle pagination anywhere in the app.

### Generic Payload Format
```ts
interface PaginatedResponse<T> {
  items: T[];           // The actual array of data objects
  page: number;         // Current page number (echoed back)
  page_size: number;    // Number of items per page (echoed back)
  total: number;        // Total number of items across all pages in the DB
  total_pages: number;  // Total calculated pages (total / page_size)
}
```

### Example Response
```json
{
  "items": [
    {
      "id": "uuid-1",
      "name": "Production",
      ...
    },
    {
      "id": "uuid-2",
      "name": "Quality Assurance",
      ...
    }
  ],
  "page": 2,
  "page_size": 5,
  "total": 32,
  "total_pages": 7
}
```

---

## Frontend Implementation Tips

1. **Calculating Next/Previous Pages:** 
   Use `page` and `total_pages` to determine if your "Next" or "Previous" buttons should be disabled.
   - `has_previous = response.page > 1`
   - `has_next = response.page < response.total_pages`

2. **Handling Empty States:**
   If `response.total == 0`, or `response.items.length === 0`, render your generic "No data found" component.

3. **Page Size Normalization:**
   Do not rely on the response array length to determine page size. If you request `page_size=50`, the backend capping it to 10 will mean `response.items` only has 10 elements, and `response.page_size` will equal 10. Always use the `response.page_size` value provided in the payload for your UI state.