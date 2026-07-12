import asyncio
import os
from database import init_user_db

async def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    for file in os.listdir(data_dir):
        if file.startswith("db_") and file.endswith(".sqlite3"):
            db_path = os.path.join(data_dir, file)
            print(f"Fixing db {db_path}")
            await init_user_db(db_path)
            print(f"Fixed {db_path}")

if __name__ == "__main__":
    asyncio.run(main())
