import sqlite3
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from render import render_pdf

app = FastAPI()

# Database setup on startup
def init_db():
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            created_at DATE
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/health")
def health_check():
    return {"status": "ok"}

class ReportRequest(BaseModel):
    force: bool = False

@app.post("/reports", status_code=status.HTTP_201_CREATED)
def generate_report(request: ReportRequest, response: Response):
    conn = sqlite3.connect("report.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Idempotency check: if report for today exists and force is not True
    if not request.force:
        cursor.execute("SELECT id FROM reports WHERE created_at = ? ORDER BY id DESC LIMIT 1", (today,))
        existing_report = cursor.fetchone()
        if existing_report:
            response.status_code = status.HTTP_200_OK
            report_id = existing_report["id"]
            conn.close()
            return {
                "id": report_id,
                "file": f"/reports/{report_id}/file"
            }
    
    # 1. Insert a new row to get an ID first (using a temporary path)
    cursor.execute("INSERT INTO reports (path, created_at) VALUES (?, ?)", ("", today))
    conn.commit()
    report_id = cursor.lastrowid
    
    # 2. Render the PDF
    pdf_path = render_pdf(report_id)
    
    # 3. Update the path in the database
    cursor.execute("UPDATE reports SET path = ? WHERE id = ?", (pdf_path, report_id))
    conn.commit()
    conn.close()
    
    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file"
    }

@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = sqlite3.connect("report.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, path, created_at FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "id": row["id"],
        "path": row["path"],
        "created_at": row["created_at"],
        "file": f"/reports/{row['id']}/file"
    }

@app.get("/reports/{report_id}/file")
def get_report_file(report_id: int):
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
        
    pdf_path = row[0]
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
        
    return FileResponse(pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path))
