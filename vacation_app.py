import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# 1. 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('vacation_system.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            vacation_type TEXT,
            start_date TEXT,
            end_date TEXT,
            reason TEXT,
            status TEXT,
            request_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 2. 신청 함수
def submit_request(name, v_type, s_date, e_date, reason):
    conn = sqlite3.connect('vacation_system.db')
    c = conn.cursor()
    req_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO requests (name, vacation_type, start_date, end_date, reason, status, request_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, v_type, str(s_date), str(e_date), reason, '대기', req_date))
    conn.commit()
    conn.close()

# 3. 상태 변경 함수
def update_status(request_id, new_status):
    conn = sqlite3.connect('vacation_system.db')
    c = conn.cursor()
    c.execute('UPDATE requests SET status = ? WHERE id = ?', (new_status, request_id))
    conn.commit()
    conn.close()

# 4. 데이터 로드 함수
def load_data(filter_status=None, filter_name=None):
    conn = sqlite3.connect('vacation_system.db')
    query = "SELECT * FROM requests"
    conditions = []
    params = []
    if filter_status:
        conditions.append("status = ?")
        params.append(filter_status)
    if filter_name:
        conditions.append("name = ?")
        params.append(filter_name)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id DESC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# === HTML 문서 양식 (들여쓰기 제거 및 CSS 최적화) ===
def create_document_html(row):
    stamp_dept = ""   
    stamp_admin = ""  
    
    # 도장 스타일
    stamp_style = "border: 3px solid #cc0000; color: #cc0000; border-radius: 50%; padding: 8px; font-weight: 900; font-size: 16px; transform: rotate(-15deg); display: inline-block;"

    if row['status'] == '승인':
        stamp_dept = f"<div style='{stamp_style}'>승인</div>"
        stamp_admin = f"<div style='{stamp_style}'>승인</div>"
    elif row['status'] == '반려':
        stamp_dept = f"<div style='{stamp_style} border-color: red; color: red;'>반려</div>"
        stamp_admin = ""

    # [중요] f-string 안의 들여쓰기를 최소화해서 HTML 인식이 잘 되게 수정함
    doc_html = f"""
<div style="border: 2px solid #e0e0e0; padding: 30px; background-color: white; color: black; font-family: 'Malgun Gothic', sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h2 style="text-align: center; color: #333; margin-bottom: 30px; letter-spacing: 2px;">휴 가 신 청 서</h2>
    
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
        <table style="border-collapse: collapse; text-align: center; border: 1px solid #333; color: black; width: 200px; background-color: white;">
            <tr>
                <td style="border: 1px solid #333; padding: 5px; background: #f0f0f0; width: 50%; font-size: 13px; font-weight: bold;">부서장</td>
                <td style="border: 1px solid #333;