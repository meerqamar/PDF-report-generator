import sqlite3
import json

def get_report_data():
    conn = sqlite3.connect("report.db")
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Total number of orders
    cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
    total_orders = cursor.fetchone()["total_orders"]
    
    # 2. Total revenue
    cursor.execute("SELECT SUM(amount) as total_revenue FROM orders")
    total_revenue = round(cursor.fetchone()["total_revenue"], 2)
    
    # 3. Top 5 products by revenue
    cursor.execute('''
        SELECT product, SUM(amount) as revenue 
        FROM orders 
        GROUP BY product 
        ORDER BY revenue DESC 
        LIMIT 5
    ''')
    top_products = [dict(row) for row in cursor.fetchall()]
    
    # 4. Orders per day for the last 7 days
    cursor.execute('''
        SELECT created_at as date, COUNT(*) as orders_count
        FROM orders
        WHERE created_at >= date('now', '-7 days')
        GROUP BY created_at
        ORDER BY created_at DESC
    ''')
    orders_per_day = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "top_products": top_products,
        "orders_per_day": orders_per_day
    }

if __name__ == "__main__":
    # Test script: print the report object as JSON
    data = get_report_data()
    print(json.dumps(data, indent=2))
