import sqlite3
import random
from datetime import datetime, timedelta

def insert_dummy_data():
    db_path = "backend/data/db_8e79381f6cbe488b8a4e21ef3beb253c.sqlite3"
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check if we already seeded transactions
    cur.execute("SELECT count(*) FROM transactions")
    if cur.fetchone()[0] > 0:
        print("Already seeded!")
        return

    # Categories
    categories_data = [
        ("Makanan", "expense", "🍔"),
        ("Transport", "expense", "🚗"),
        ("Belanja", "expense", "🛍️"),
        ("Tagihan", "expense", "🔌"),
        ("Gaji", "income", "💰"),
        ("Bonus", "income", "🎁"),
    ]
    for name, t, icon in categories_data:
        cur.execute("INSERT INTO categories (name, type, icon) VALUES (?, ?, ?)", (name, t, icon))
        
    # Fund Source
    cur.execute("INSERT INTO fund_sources (name, type, icon, initial_balance) VALUES (?, ?, ?, ?)", 
                ("Bank BCA", "bank", "🏦", 15000000))
    fund_source_id = cur.lastrowid
    
    # Transactions
    today = datetime.now()
    transactions = []
    
    for month_offset in range(6):
        base_date = today - timedelta(days=30 * month_offset)
        
        # Salary
        transactions.append((
            "income", 10000000, "Gaji", "Gaji Bulanan", 
            base_date.replace(day=1).strftime("%Y-%m-%d"), fund_source_id
        ))
        
        num_expenses = 30 if month_offset == 0 else 10
        
        for _ in range(num_expenses):
            random_day = random.randint(1, 28)
            tx_date = base_date.replace(day=random_day)
            cat = random.choice(["Makanan", "Transport", "Belanja", "Tagihan"])
            
            if cat == "Makanan":
                amt = random.randint(20, 150) * 1000
            elif cat == "Transport":
                amt = random.randint(10, 50) * 1000
            elif cat == "Belanja":
                amt = random.randint(100, 1500) * 1000
            else:
                amt = random.randint(50, 500) * 1000
                
            transactions.append((
                "expense", amt, cat, f"Pengeluaran {cat}", 
                tx_date.strftime("%Y-%m-%d"), fund_source_id
            ))
            
    cur.executemany("""
        INSERT INTO transactions (type, amount, category, description, date, fund_source_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, transactions)
    
    conn.commit()
    conn.close()
    print("Seed complete.")

if __name__ == "__main__":
    insert_dummy_data()
