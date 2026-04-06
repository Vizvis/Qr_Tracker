"""Reset the local QR Tracker database and seed test data."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DatabaseConfig
from models.db_models import Base, Department, DepartmentStatus, ProducedItems, QRCode, Remarks, RoleLevel, User
from auth.jwt_auth import JWTAuth

HEAD_REVISION = "c89a2607b01e"


def get_engine():
    return create_engine(DatabaseConfig.get_database_url_sync(), future=True)


def reset_schema(engine) -> None:
    current_revision = None
    with engine.connect() as connection:
        current_revision = connection.execute(text("select version_num from alembic_version limit 1")).scalar_one_or_none()

    print(f"Current alembic revision: {current_revision or 'none'}")
    print("Dropping application tables and recreating schema from current models...")
    Base.metadata.drop_all(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine, checkfirst=True)


def seed_data(engine) -> None:
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    now = datetime.utcnow()

    admin = User(
        id=uuid4(),
        name="Vishal",
        phone_number="7550226829",
        email="vishal@example.com",
        hashed_password=JWTAuth.hash_password("Vishal123"),
        role=RoleLevel.ADMIN,
        is_active=True,
        created_at=now - timedelta(hours=3),
    )
    supervisor = User(
        id=uuid4(),
        name="Arjun Singh",
        phone_number="9123456780",
        email="arjun.singh@example.com",
        hashed_password=JWTAuth.hash_password("Arjun123"),
        role=RoleLevel.SUPERVISOR,
        is_active=True,
        created_at=now - timedelta(hours=2),
    )

    extra_users = [
        User(
            id=uuid4(),
            name="Karan Mehta",
            phone_number="9000000001",
            email="karan.mehta@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.OPERATOR,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=50),
        ),
        User(
            id=uuid4(),
            name="Neha Sharma",
            phone_number="9000000002",
            email="neha.sharma@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.VIEWER,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=45),
        ),
        User(
            id=uuid4(),
            name="Amit Verma",
            phone_number="9000000003",
            email="amit.verma@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.OPERATOR,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=40),
        ),
        User(
            id=uuid4(),
            name="Pooja Iyer",
            phone_number="9000000004",
            email="pooja.iyer@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.VIEWER,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=35),
        ),
        User(
            id=uuid4(),
            name="Rahul Das",
            phone_number="9000000005",
            email="rahul.das@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.OPERATOR,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=30),
        ),
        User(
            id=uuid4(),
            name="Sneha Patil",
            phone_number="9000000006",
            email="sneha.patil@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.VIEWER,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=25),
        ),
        User(
            id=uuid4(),
            name="Vivek Kumar",
            phone_number="9000000007",
            email="vivek.kumar@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.OPERATOR,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=20),
        ),
        User(
            id=uuid4(),
            name="Ananya Rao",
            phone_number="9000000008",
            email="ananya.rao@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.VIEWER,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=15),
        ),
        User(
            id=uuid4(),
            name="Farhan Ali",
            phone_number="9000000009",
            email="farhan.ali@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.OPERATOR,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=10),
        ),
        User(
            id=uuid4(),
            name="Meera Joshi",
            phone_number="9000000010",
            email="meera.joshi@example.com",
            hashed_password=JWTAuth.hash_password("User1234"),
            role=RoleLevel.VIEWER,
            is_active=True,
            created_at=now - timedelta(hours=1, minutes=5),
        ),
    ]

    department_one = Department(
        id=uuid4(),
        name="hostelname_101",
        sequence_order=1,
        status=DepartmentStatus.ACTIVE,
        head_of_department=supervisor.id,
        created_on=now - timedelta(days=2),
    )
    department_two = Department(
        id=uuid4(),
        name="hostelname_102",
        sequence_order=2,
        status=DepartmentStatus.ACTIVE,
        head_of_department=None,
        created_on=now - timedelta(days=2),
    )
    department_three = Department(
        id=uuid4(),
        name="hostelname_103",
        sequence_order=3,
        status=DepartmentStatus.ACTIVE,
        head_of_department=None,
        created_on=now - timedelta(days=2),
    )

    qr_one = QRCode(
        id="10000001",
        status="active",
        registered_by=admin.id,
        enabled_by=supervisor.id,
        enabled_at=now - timedelta(hours=1),
        disabled_by=None,
        disabled_at=None,
        created_at=now - timedelta(hours=2),
        notes="Seed QR for hostelname_101",
    )
    qr_two = QRCode(
        id="10000002",
        status="inactive",
        registered_by=admin.id,
        enabled_by=None,
        enabled_at=None,
        disabled_by=supervisor.id,
        disabled_at=now - timedelta(minutes=20),
        created_at=now - timedelta(hours=1, minutes=30),
        notes="Seed QR for hostelname_102",
    )

    remark_one = Remarks(
        id=uuid4(),
        qr_id=qr_one.id,
        item_id="ITEM-001",
        department_id=department_one.id,
        general_remarks="Initial inspection passed.",
        issue_remarks=None,
        custom_data={"room": department_one.name, "shift": "A"},
        remarks_history=[],
        remark_by=admin.id,
        remark_updated=supervisor.id,
        created_at=now - timedelta(minutes=55),
        updated_at=now - timedelta(minutes=50),
    )
    remark_two = Remarks(
        id=uuid4(),
        qr_id=qr_one.id,
        item_id="ITEM-001",
        department_id=department_two.id,
        general_remarks="Packed and ready for dispatch.",
        issue_remarks="Label alignment corrected.",
        custom_data={"room": department_two.name, "batch": "B-01"},
        remarks_history=[],
        remark_by=supervisor.id,
        remark_updated=supervisor.id,
        created_at=now - timedelta(minutes=45),
        updated_at=now - timedelta(minutes=40),
    )
    remark_three = Remarks(
        id=uuid4(),
        qr_id=qr_two.id,
        item_id="ITEM-002",
        department_id=department_three.id,
        general_remarks="Needs recheck before release.",
        issue_remarks="Minor surface scratches noted.",
        custom_data={"room": department_three.name, "priority": "high"},
        remarks_history=[],
        remark_by=admin.id,
        remark_updated=admin.id,
        created_at=now - timedelta(minutes=35),
        updated_at=now - timedelta(minutes=30),
    )

    extra_remarks = [
        Remarks(
            id=uuid4(),
            qr_id=qr_one.id,
            item_id="ITEM-003",
            department_id=department_one.id,
            general_remarks="Material received and checked.",
            issue_remarks=None,
            custom_data={"room": department_one.name, "inspector": "Karan"},
            remarks_history=[],
            remark_by=admin.id,
            remark_updated=admin.id,
            created_at=now - timedelta(minutes=29),
            updated_at=now - timedelta(minutes=28),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_one.id,
            item_id="ITEM-003",
            department_id=department_two.id,
            general_remarks="Packing started.",
            issue_remarks="Box size mismatch corrected.",
            custom_data={"room": department_two.name, "stage": "packing"},
            remarks_history=[],
            remark_by=supervisor.id,
            remark_updated=supervisor.id,
            created_at=now - timedelta(minutes=27),
            updated_at=now - timedelta(minutes=26),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_one.id,
            item_id="ITEM-004",
            department_id=department_three.id,
            general_remarks="Ready for quality check.",
            issue_remarks=None,
            custom_data={"room": department_three.name, "priority": "medium"},
            remarks_history=[],
            remark_by=admin.id,
            remark_updated=supervisor.id,
            created_at=now - timedelta(minutes=25),
            updated_at=now - timedelta(minutes=24),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_two.id,
            item_id="ITEM-004",
            department_id=department_one.id,
            general_remarks="Surface cleaned.",
            issue_remarks="Dust found and removed.",
            custom_data={"room": department_one.name, "cleaned": True},
            remarks_history=[],
            remark_by=supervisor.id,
            remark_updated=supervisor.id,
            created_at=now - timedelta(minutes=23),
            updated_at=now - timedelta(minutes=22),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_two.id,
            item_id="ITEM-005",
            department_id=department_two.id,
            general_remarks="Assembly completed.",
            issue_remarks=None,
            custom_data={"room": department_two.name, "batch": "B-02"},
            remarks_history=[],
            remark_by=admin.id,
            remark_updated=admin.id,
            created_at=now - timedelta(minutes=21),
            updated_at=now - timedelta(minutes=20),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_two.id,
            item_id="ITEM-005",
            department_id=department_three.id,
            general_remarks="Final visual check done.",
            issue_remarks="Minor dent documented.",
            custom_data={"room": department_three.name, "severity": "low"},
            remarks_history=[],
            remark_by=supervisor.id,
            remark_updated=admin.id,
            created_at=now - timedelta(minutes=19),
            updated_at=now - timedelta(minutes=18),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_one.id,
            item_id="ITEM-006",
            department_id=department_one.id,
            general_remarks="Tag verified.",
            issue_remarks=None,
            custom_data={"room": department_one.name, "tag_status": "ok"},
            remarks_history=[],
            remark_by=admin.id,
            remark_updated=admin.id,
            created_at=now - timedelta(minutes=17),
            updated_at=now - timedelta(minutes=16),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_one.id,
            item_id="ITEM-006",
            department_id=department_three.id,
            general_remarks="Moved to dispatch lane.",
            issue_remarks=None,
            custom_data={"room": department_three.name, "lane": "L-4"},
            remarks_history=[],
            remark_by=supervisor.id,
            remark_updated=supervisor.id,
            created_at=now - timedelta(minutes=15),
            updated_at=now - timedelta(minutes=14),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_two.id,
            item_id="ITEM-007",
            department_id=department_one.id,
            general_remarks="Rework approved.",
            issue_remarks="Screw alignment fixed.",
            custom_data={"room": department_one.name, "rework": "approved"},
            remarks_history=[],
            remark_by=admin.id,
            remark_updated=supervisor.id,
            created_at=now - timedelta(minutes=13),
            updated_at=now - timedelta(minutes=12),
        ),
        Remarks(
            id=uuid4(),
            qr_id=qr_two.id,
            item_id="ITEM-008",
            department_id=department_two.id,
            general_remarks="Shipment hold removed.",
            issue_remarks=None,
            custom_data={"room": department_two.name, "hold": False},
            remarks_history=[],
            remark_by=supervisor.id,
            remark_updated=supervisor.id,
            created_at=now - timedelta(minutes=11),
            updated_at=now - timedelta(minutes=10),
        ),
    ]

    produced_one = ProducedItems(
        produced_id=uuid4(),
        qr_id=qr_one.id,
        item_id="ITEM-001",
        department_name=department_one.name,
        general_remarks="Initial inspection passed.",
        issue_remarks=None,
        created_by=admin.id,
        updated_by=supervisor.id,
        remark_by=admin.id,
        remark_updated=supervisor.id,
        created_at=now - timedelta(minutes=25),
    )
    produced_two = ProducedItems(
        produced_id=uuid4(),
        qr_id=qr_two.id,
        item_id="ITEM-002",
        department_name=department_three.name,
        general_remarks="Needs recheck before release.",
        issue_remarks="Minor surface scratches noted.",
        created_by=supervisor.id,
        updated_by=admin.id,
        remark_by=admin.id,
        remark_updated=admin.id,
        created_at=now - timedelta(minutes=15),
    )

    with session_factory() as session:
        session.add_all(
            [
                admin,
                supervisor,
                *extra_users,
                department_one,
                department_two,
                department_three,
                qr_one,
                qr_two,
                remark_one,
                remark_two,
                remark_three,
                *extra_remarks,
                produced_one,
                produced_two,
            ]
        )
        session.commit()

    print("Seeded users, departments, QR codes, remarks, and produced items.")
    print("Test credentials:")
    print("- vishal@example.com / Vishal123")
    print("- arjun.singh@example.com / Arjun123")


def stamp_head(engine) -> None:
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", DatabaseConfig.get_database_url_sync())
    try:
        command.stamp(cfg, HEAD_REVISION)
    except Exception:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM alembic_version"))
            connection.execute(text("INSERT INTO alembic_version (version_num) VALUES (:version_num)"), {"version_num": HEAD_REVISION})
    print(f"Alembic version set to {HEAD_REVISION}.")


def main() -> None:
    engine = get_engine()
    reset_schema(engine)
    seed_data(engine)
    stamp_head(engine)

    with engine.connect() as connection:
        revision = connection.execute(text("select version_num from alembic_version limit 1")).scalar_one_or_none()
        counts = {
            table: connection.execute(text(f'SELECT count(*) FROM "{table}"')).scalar_one()
            for table in ["users", "department", "qr_codes", "remarks", "produced_items"]
        }

    print(f"Verified alembic revision: {revision}")
    for table, count in counts.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
