import asyncio
import sqlite3
import os
from database import init_user_db

async def main():
    auth_db_path = os.path.join(os.path.dirname(__file__), "data", "auth.db")
    conn = sqlite3.connect(auth_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, db_path FROM users")
    users = cursor.fetchall()
    conn.close()

    for user_id, email, db_path in users:
        print(f"Checking user {email} (ID {user_id}) with db {db_path}")
        try:
            await init_user_db(db_path)
            print(f"-> Successfully initialized/fixed {db_path}")
        except Exception as e:
            print(f"-> Failed to initialize {db_path}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
