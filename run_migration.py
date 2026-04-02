import asyncio
from sqlalchemy import text
from db_handler.database import db_manager

async def run_data_migrations():
    print("Connecting to DB to run data migrations...")
    async with db_manager.session_factory() as db:
        # Migrate QR status
        try:
            await db.execute(text("UPDATE qr_codes SET status = 'inactive' WHERE status = 'pending'"))
            print("1. Migrated qr_codes status from 'pending' to 'inactive'")
        except Exception as e:
            print("Error updating qr_codes:", e)
            
        await db.commit()

if __name__ == "__main__":
    asyncio.run(run_data_migrations())