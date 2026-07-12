import asyncio
import uuid
import random
import os
from datetime import datetime, timedelta

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import AuthAsyncSessionFactory, init_user_db, DATA_DIR
from backend.models.user import User
from backend.services.auth_service import hash_password
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.models.transaction import Transaction
from backend.models.fund_source import FundSource
from backend.models.category import Category
from backend.models.budget import Budget, CategoryBudget

async def seed_data():
    email = "dummy@example.com"
    password = "password123"
    
    # 1. Create User in Master DB
    async with AuthAsyncSessionFactory() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user:
            user = User(
                email=email,
                hashed_password=hash_password(password),
                full_name="Akun Dummy",
                nickname="Dummy",
                db_path=os.path.join(DATA_DIR, f"db_{uuid.uuid4().hex}.sqlite3")
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"Created user: {user.email} with DB Path {user.db_path}")
        else:
            print(f"User {user.email} already exists with DB Path {user.db_path}")

    # 2. Init User DB
    await init_user_db(user.db_path)
    
    # 3. Create Session for User DB
    user_engine = create_async_engine(f"sqlite+aiosqlite:///{user.db_path}", future=True)
    UserSession = sessionmaker(
        user_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with UserSession() as session:
        # Check if already seeded
        result = await session.execute(select(FundSource))
        existing_fs = result.scalars().all()
        
        fs_id = None
        if not existing_fs:
            # Seed Categories
            categories_data = [
                ("Makanan", "expense", "🍔"),
                ("Transport", "expense", "🚗"),
                ("Belanja", "expense", "🛍️"),
                ("Tagihan", "expense", "🔌"),
                ("Gaji", "income", "💰"),
                ("Bonus", "income", "🎁"),
            ]
            
            for name, type_val, icon in categories_data:
                session.add(Category(name=name, type=type_val, icon=icon))
            
            await session.commit()
            
            # Seed Fund Source
            fs = FundSource(
                name="Bank BCA",
                type="bank",
                icon="🏦",
                initial_balance=15000000
            )
            session.add(fs)
            await session.commit()
            await session.refresh(fs)
            fs_id = fs.id
        else:
            print("Fund Source and Categories already seeded.")
            fs_id = existing_fs[0].id

        # Seed Transactions if not already seeded
        result_tx = await session.execute(select(Transaction))
        existing_tx = result_tx.scalars().all()
        
        today = datetime.now()
        if not existing_tx:
            transactions = []
            
            def rand_amount(min_val, max_val):
                return random.randint(min_val // 1000, max_val // 1000) * 1000

            for month_offset in range(6):
                base_date = today - timedelta(days=30 * month_offset)
                
                transactions.append(Transaction(
                    type="income",
                    amount=10000000,
                    category="Gaji",
                    description="Gaji Bulanan",
                    date=base_date.replace(day=1).date(),
                    fund_source_id=fs_id
                ))
                
                num_expenses = 30 if month_offset == 0 else 10
                
                for _ in range(num_expenses):
                    random_day = random.randint(1, 28)
                    tx_date = base_date.replace(day=random_day)
                    
                    cat = random.choice(["Makanan", "Transport", "Belanja", "Tagihan"])
                    
                    if cat == "Makanan":
                        amt = rand_amount(20000, 150000)
                    elif cat == "Transport":
                        amt = rand_amount(10000, 50000)
                    elif cat == "Belanja":
                        amt = rand_amount(100000, 1500000)
                    else:
                        amt = rand_amount(50000, 500000)
                        
                    transactions.append(Transaction(
                        type="expense",
                        amount=amt,
                        category=cat,
                        description=f"Pengeluaran {cat}",
                        date=tx_date.date(),
                        fund_source_id=fs_id
                    ))
                    
            session.add_all(transactions)
            await session.commit()
            print("Successfully seeded 6 months of transactions!")
        else:
            print("Transactions already seeded.")

        # Seed Budgets if not already seeded
        result_b = await session.execute(select(Budget))
        existing_b = result_b.scalars().all()
        if not existing_b:
            print("Seeding dummy budgets...")
            
            # Current Month budget
            b_current = Budget(month="ALL", amount=8000000)
            session.add(b_current)
            await session.flush()
            
            session.add(CategoryBudget(budget_id=b_current.id, category_name="Makanan", amount=2000000))
            session.add(CategoryBudget(budget_id=b_current.id, category_name="Transport", amount=800000))
            session.add(CategoryBudget(budget_id=b_current.id, category_name="Belanja", amount=3000000))
            session.add(CategoryBudget(budget_id=b_current.id, category_name="Tagihan", amount=1500000))
            
            await session.commit()
            print("Successfully seeded dummy budgets!")
        else:
            print("Budgets already seeded.")

if __name__ == "__main__":
    asyncio.run(seed_data())
