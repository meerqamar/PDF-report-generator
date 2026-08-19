# PDF Report Generator

A backend API pipeline that queries a SQLite database, renders an HTML report, stores it as a PDF using Playwright, and serves it to users by link.

## Dataset
I chose **The Little Shop**, a randomly seeded dataset containing 200 orders across 6 products over the last 30 days.

## How to Run

1. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Seed the Database:**
   ```powershell
   python seed.py
   ```

3. **Start the API Server:**
   ```powershell
   uvicorn server:app --port 3000
   ```

## Aggregation SQL
```sql
SELECT COUNT(*) as total_orders FROM orders;

SELECT SUM(amount) as total_revenue FROM orders;

SELECT product, SUM(amount) as revenue 
FROM orders 
GROUP BY product 
ORDER BY revenue DESC 
LIMIT 5;

SELECT created_at as date, COUNT(*) as orders_count
FROM orders
WHERE created_at >= date('now', '-7 days')
GROUP BY created_at
ORDER BY created_at DESC;
```

## Download Proof
```bash
curl.exe -i -X POST http://localhost:3000/reports
# HTTP/1.1 201 Created
# {"id":1,"file":"/reports/1/file"}

curl.exe -o my-report.pdf http://localhost:3000/reports/1/file
```

## Conceptual Answers

**Stage 4 (Background Jobs):** 
I would move this work out of the request and into a background job when the PDF generation takes too long (e.g., several seconds or more), because keeping the client waiting on a single HTTP connection is fragile and vulnerable to timeouts.

**Stage 5 (Idempotency):**
This check protects against accidental duplicate requests, such as a user double-clicking the "Generate" button. A real-world example where missing this check costs money is sending an invoice email: generating two reports means emailing the customer twice, which looks unprofessional and could result in duplicate charges or confusion.

## PDF Screenshot
![PDF Screenshot](reports/screenshot.png)
