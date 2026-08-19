import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from report import get_report_data

def build_html(data):
    today = datetime.now().strftime("%Y-%m-%d")
    days = data.get("days_parameter", 7)
    
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
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            @page {{
                margin: 20mm;
                @bottom-right {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-family: 'Inter', sans-serif;
                    font-size: 10px;
                    color: #666;
                }}
                @bottom-left {{
                    content: "The Little Shop Report";
                    font-family: 'Inter', sans-serif;
                    font-size: 10px;
                    color: #666;
                }}
            }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                padding: 0; 
                margin: 0;
                color: #2c3e50;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }}
            .header h1 {{ 
                color: #2c3e50; 
                margin: 0;
                font-size: 28px;
            }}
            .header .logo {{
                font-size: 24px;
                font-weight: 700;
                color: #3498db;
            }}
            .summary {{ 
                display: flex; 
                gap: 20px; 
                margin-bottom: 40px; 
            }}
            .stat {{ 
                background: linear-gradient(135deg, #f6f8f9 0%, #e5ebee 100%);
                padding: 20px; 
                border-radius: 12px; 
                flex: 1;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }}
            .stat h3 {{
                margin: 0 0 10px 0;
                font-size: 14px;
                color: #7f8c8d;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .stat p {{
                margin: 0;
                font-size: 28px;
                font-weight: 700;
                color: #2c3e50;
            }}
            h2 {{
                color: #34495e;
                margin-bottom: 15px;
                font-size: 20px;
                border-bottom: 1px solid #ecf0f1;
                padding-bottom: 8px;
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin-bottom: 40px; 
                font-size: 14px;
            }}
            th, td {{ 
                border-bottom: 1px solid #ecf0f1; 
                padding: 12px 15px; 
                text-align: left; 
            }}
            th {{ 
                background-color: #f8f9fa; 
                font-weight: 600;
                color: #34495e;
            }}
            tbody tr:nth-of-type(even) {{
                background-color: #fcfcfc;
            }}
            /* Fix page breaks */
            tr {{ break-inside: avoid; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>Sales Report</h1>
                <p style="margin: 5px 0 0 0; color: #7f8c8d;">Generated on {today} • Last {days} days</p>
            </div>
            <div class="logo">🛍️ The Little Shop</div>
        </div>
        
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
        
        <h2>Orders Per Day (Last {days} Days)</h2>
        <table>
            <thead>
                <tr><th>Date</th><th>Orders</th></tr>
            </thead>
            <tbody>
                {orders_rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html

def render_pdf(report_id="test", days=7):
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    
    data = get_report_data(days=days)
    html_content = build_html(data)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"sales-report-{today}-{report_id}.pdf"
    pdf_path = f"reports/{filename}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            display_header_footer=True, # enables the @page headers/footers
            header_template="<span></span>", # Empty header allows @page CSS to take over
            footer_template="<span></span>", # Empty footer allows @page CSS to take over
            margin={"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"}
        )
        browser.close()
        
    return pdf_path

if __name__ == "__main__":
    print(f"PDF generated successfully at {render_pdf()}")
