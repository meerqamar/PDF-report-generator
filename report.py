import sqlite3
import json

def get_report_data(days=7):
    conn = sqlite3.connect("report.db")
    # Return rows as dictionaries
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We filter all data by the last `days` days
    date_filter = f"'-{days} days'"
    query_params = (f"-{days} days",)
    
    # 1. Total number of orders
    cursor.execute("SELECT COUNT(*) as total_orders FROM orders WHERE created_at >= date('now', ?)", query_params)
    total_orders = cursor.fetchone()["total_orders"]
    
    # 2. Total revenue
    cursor.execute("SELECT SUM(amount) as total_revenue FROM orders WHERE created_at >= date('now', ?)", query_params)
    revenue_val = cursor.fetchone()["total_revenue"]
    total_revenue = round(revenue_val, 2) if revenue_val else 0.0
    
    # 3. Top 5 products by revenue
    cursor.execute('''
        SELECT product, SUM(amount) as revenue 
        FROM orders 
        WHERE created_at >= date('now', ?)
        GROUP BY product 
        ORDER BY revenue DESC 
        LIMIT 5
    ''', query_params)
    top_products = [dict(row) for row in cursor.fetchall()]
    
    # 4. Orders per day for the last X days
    cursor.execute('''
        SELECT created_at as date, COUNT(*) as orders_count
        FROM orders
        WHERE created_at >= date('now', ?)
        GROUP BY created_at
        ORDER BY created_at DESC
    ''', query_params)
    orders_per_day = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "days_parameter": days,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "top_products": top_products,
        "orders_per_day": orders_per_day
    }

if __name__ == "__main__":
    # Test script: print the report object as JSON
    data = get_report_data(days=30)
    print(json.dumps(data, indent=2))
