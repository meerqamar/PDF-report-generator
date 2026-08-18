import sqlite3
import random
from datetime import datetime, timedelta

def seed_database():
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            product TEXT,
            amount REAL,
            created_at DATE
        )
    ''')

    # Delete existing rows to make it idempotent
    cursor.execute('DELETE FROM orders')

    products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Desk"]
    customers = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank"]
    
    # Generate ~200 orders
    num_orders = 200
    today = datetime.now()
    
    orders = []
    for _ in range(num_orders):
        customer = random.choice(customers)
        product = random.choice(products)
        amount = round(random.uniform(5.0, 200.0), 2)
        days_ago = random.randint(0, 30)
        created_at = (today - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        orders.append((customer, product, amount, created_at))

    cursor.executemany(
        'INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)',
        orders
    )

    conn.commit()
    
    # Verify count
    cursor.execute('SELECT COUNT(*) FROM orders')
    count = cursor.fetchone()[0]
    print(f"Seeded report.db with {count} orders.")
    
    conn.close()

if __name__ == "__main__":
    seed_database()
