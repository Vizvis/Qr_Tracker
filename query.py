
import asyncio
import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def run():
    conn = await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST")
    )
    rows = await conn.fetch('''
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'qr_codes'
    ''')
    for r in rows:
        print(r['column_name'], r['data_type'])
    await conn.close()

asyncio.run(run())

