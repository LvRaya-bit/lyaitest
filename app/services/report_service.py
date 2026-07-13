# app/services/report_service.py
# 报告服务：将测试报告存入 SQLite 数据库

import uuid
from datetime import datetime
from app.database import get_connection

def save_report(report_data: dict):
    """保存测试报告到 SQLite"""
    report_id = str(uuid.uuid4())[:8]
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO reports (
            id, session_id, test_type, url, status_code,
            response_time, title, screenshot, error, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id,
        report_data.get("session_id", "unknown"),
        report_data.get("test_type", "unknown"),
        report_data.get("url", ""),
        report_data.get("status_code"),
        report_data.get("response_time"),
        report_data.get("title"),
        report_data.get("screenshot"),
        report_data.get("error"),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    return report_id

def get_all_reports():
    """获取所有测试报告"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_reports_by_session(session_id: str):
    """根据会话ID获取报告"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reports WHERE session_id = ? ORDER BY created_at DESC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_report_by_id(report_id: str):
    """根据报告ID获取单条报告"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None