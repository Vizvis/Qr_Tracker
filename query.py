
import asyncio
import asyncpg
async def run():
    conn = await asyncpg.connect(user='postgres', password='sivu@2004', database='QR_tracker', host='localhost')
    rows = await conn.fetch('''SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \\'qr_codes\\' ''')
    for r in rows:
        print(r['column_name'], r['data_type'])
    await conn.close()
asyncio.run(run())

