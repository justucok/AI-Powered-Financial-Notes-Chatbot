import asyncio
from backend.database import init_auth_db, AuthAsyncSessionFactory
from backend.services.auth_service import register_user
from backend.schemas.auth import RegisterRequest

async def main():
    await init_auth_db()
    async with AuthAsyncSessionFactory() as session:
        data = RegisterRequest(email="test999@example.com", full_name="Test", nickname="Test", password="password123")
        try:
            res = await register_user(session, data)
            print("SUCCESS:", res)
        except Exception as e:
            print(f"Exception: {type(e).__name__} - {e}")

if __name__ == "__main__":
    asyncio.run(main())
