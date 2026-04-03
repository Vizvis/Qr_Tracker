# Backend Responses to Frontend Queries

## 1. "Invalid Date" on Frontend (Session Timestamps)
**Response:**
FastAPI and Pydantic generally serialize `datetime` objects to ISO 8601 strings automatically. However, if the datetimes stored in PostgreSQL are naive (without timezone info), they might not append the `Z` suffix. 

To fix this natively on the backend, we can enforce timezone-aware datetimes in our system. That means converting our UTC times to include timezone information before Pydantic serializes them, which will produce proper `YYYY-MM-DDTHH:MM:SS.sssZ` formats that Safari and older browsers can parse correctly. 
We will verify the Pydantic schemas (like `SessionResponse`) and ensure that fields like `created_at` are properly annotated with timezone-aware datetimes, or we will add a custom JSON encoder/Pydantic field validator to stringify datetime fields explicitly to Javascript-compatible ISO 8601 strings.

## 2. Handling "Duplicate update" & Remark Revision History
**Response:**
We will implement the **"Single-Column History Append"** approach as requested. 
1. We will add a `remarks_history` column to the `remarks` table using PostgreSQL's `JSONB` type. This is the cleanest approach and ensures the history is structured and easily parsed by the frontend.
2. We will expose/update the `PUT /api/remarks/{remark_id}` endpoint.
3. Upon receiving an update, the backend logic will:
   - Extract the current `general_remarks`, `issue_remarks`, and the last updated timestamp.
   - Append this previous state as a JSON object into the `remarks_history` JSONB array.
   - Replace the main `general_remarks` and `issue_remarks` with the newly provided data.
4. The `GET` endpoints for remarks will include this `remarks_history` JSON array, allowing your UI to instantly render the revision history timeline.

## 3. API Schema & Database Tables Documentation
**Response:**
Since this project uses **FastAPI**, we have auto-generated OpenAPI documentation that will always be 100% accurate and up to date with the latest code, rather than a manually maintained markdown file that can fall out of sync.

You have a few ways to access this:
1. **Interactive Swagger UI:** Run the backend server locally and navigate to `http://localhost:8000/docs` (depending on the port in use). All schemas, endpoints, methods, and expected JSON request/response formats are fully interactive here.
2. **ReDoc:** Navigate to `http://localhost:8000/redoc` for an alternative, highly readable documentation format.
3. **OpenAPI JSON:** The raw schema is available at `http://localhost:8000/openapi.json` and a static copy has been saved as `openapi_schema.json` in the root of the backend repository. You can use this file directly with AI tools or API client generators (like openapi-typescript-codegen) to automatically generate your frontend types and fetch functions.
