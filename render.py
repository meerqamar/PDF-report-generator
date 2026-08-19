import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from report import get_report_data

def build_html(data):
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Build Top 5 products table rows
    top_5_rows = ""
    for p in data["top_products"]:
        top_5_rows += f"<tr><td>{p['product']}</td><td>${p['revenue']:,.2f}</td></tr>\n"
        
    # Build Orders per day table rows
    orders_rows = ""
    for o in data["orders_per_day"]:
        orders_rows += f"<tr><td>{o['date']}</td><td>{o['orders_count']}</td></tr>\n"
        
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sales Report</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; }}
            h1 {{ color: #333; }}
            .summary {{ display: flex; gap: 40px; margin-bottom: 30px; }}
            .stat {{ background: #f4f4f4; padding: 15px; border-radius: 8px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #eee; }}
            /* Fix page breaks */
            tr {{ break-inside: avoid; }}
        </style>
    </head>
    <body>
        <h1>Sales Report - {today}</h1>
        
        <div class="summary">
            <div class="stat">
                <h3>Total Orders</h3>
                <p>{data['total_orders']}</p>
            </div>
            <div class="stat">
                <h3>Total Revenue</h3>
                <p>${data['total_revenue']:,.2f}</p>
            </div>
        </div>
        
        <h2>Top 5 Products</h2>
        <table>
            <thead>
                <tr><th>Product</th><th>Revenue</th></tr>
            </thead>
            <tbody>
                {top_5_rows}
            </tbody>
        </table>
        
        <!-- Long table to test page breaks -->
        <h2>Orders Per Day (Last 7 Days)</h2>
        <table>
            <thead>
                <tr><th>Date</th><th>Orders</th></tr>
            </thead>
            <tbody>
                {orders_rows}
                <!-- Replicate rows to force a page break intentionally for testing Stage 3 -->
                {orders_rows * 10}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html

def render_pdf(report_id="test"):
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    data = get_report_data()
    html_content = build_html(data)
    
    pdf_path = f"reports/{report_id}.pdf"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True
        )
        browser.close()
        
    return pdf_path

if __name__ == "__main__":
    print(f"PDF generated successfully at {render_pdf()}")
