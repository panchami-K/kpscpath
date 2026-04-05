import asyncpg
import asyncio

async def check_users():
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        database="kpscpath",
        user="postgres",
        password="password"
    )
    
    users = await conn.fetch("SELECT * FROM users")
    print("\nUsers in PostgreSQL database:\n")
    for user in users:
        print(user)
    
    await conn.close()

asyncio.run(check_users())
