"""Ensure department enums in PostgreSQL match current code values."""
from pathlib import Path
import sys

from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DatabaseConfig
from models.db_models.enums import DepartmentEnum, DepartmentStatus


def _quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _enum_exists(conn, enum_name: str) -> bool:
    result = conn.execute(
        text(
            """
            SELECT 1
            FROM pg_type t
            JOIN pg_namespace n ON n.oid = t.typnamespace
            WHERE t.typname = :enum_name
            LIMIT 1
            """
        ),
        {"enum_name": enum_name},
    )
    return result.scalar() is not None


def _create_enum(conn, enum_name: str, values: list[str]) -> None:
    values_sql = ", ".join(_quote(v) for v in values)
    conn.execute(text(f"CREATE TYPE {enum_name} AS ENUM ({values_sql})"))


def _add_missing_values(conn, enum_name: str, values: list[str]) -> None:
    for value in values:
        conn.execute(text(f"ALTER TYPE {enum_name} ADD VALUE IF NOT EXISTS {_quote(value)}"))


def sync_department_enums() -> None:
    engine = create_engine(DatabaseConfig.get_database_url_sync())

    department_values = [item.value for item in DepartmentEnum]
    status_values = [item.value for item in DepartmentStatus]

    with engine.begin() as conn:
        if not _enum_exists(conn, "departmentenum"):
            _create_enum(conn, "departmentenum", department_values)
            print("Created enum: departmentenum")
        else:
            print("Enum exists: departmentenum")
        _add_missing_values(conn, "departmentenum", department_values)

        if not _enum_exists(conn, "departmentstatus"):
            _create_enum(conn, "departmentstatus", status_values)
            print("Created enum: departmentstatus")
        else:
            print("Enum exists: departmentstatus")
        _add_missing_values(conn, "departmentstatus", status_values)

    print("Department enums are synced with current code values.")


if __name__ == "__main__":
    sync_department_enums()
