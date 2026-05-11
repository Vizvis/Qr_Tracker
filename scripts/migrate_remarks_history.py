import asyncio
import sys
import os

from sqlalchemy.future import select

# Add the project directory to sys.path so we can import from models & db_handler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_handler.database import db_manager
from models.db_models.remarks import Remarks
from models.db_models.remarks_audit_log import RemarksAuditLog
from datetime import datetime

async def migrate_remarks_history():
    print("Connecting to database...")
    async with db_manager.session_factory() as db:
        print("Fetching remarks with history...")
        result = await db.execute(select(Remarks).filter(Remarks.remarks_history != None))
        remarks = result.scalars().all()
        
        count = 0
        for remark in remarks:
            if remark.remarks_history and isinstance(remark.remarks_history, list):
                for snapshot in remark.remarks_history:
                    # changed_at must be parsed if it's string, or just fallback
                    changed_at_val = snapshot.get("changed_at")
                    if isinstance(changed_at_val, str):
                        try:
                            changed_at_parsed = datetime.fromisoformat(changed_at_val.replace("Z", "+00:00"))
                            # Make naive for DB if required, or keep it
                            changed_at_parsed = changed_at_parsed.replace(tzinfo=None)
                        except ValueError:
                            changed_at_parsed = datetime.utcnow()
                    elif isinstance(changed_at_val, datetime):
                        changed_at_parsed = changed_at_val
                    else:
                        changed_at_parsed = datetime.utcnow()
                        
                    changed_by_val = snapshot.get("changed_by")
                    
                    log = RemarksAuditLog(
                        remark_id=remark.id,
                        snapshot=snapshot,
                        changed_by=changed_by_val,
                        changed_at=changed_at_parsed
                    )
                    db.add(log)
                    count += 1
                    
        print(f"Migrating {count} audit logs...")
        await db.commit()
        print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate_remarks_history())