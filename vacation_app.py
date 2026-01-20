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

# === HTML 문서 양식 (결재란 수정됨!) ===
def create_document_html(row):
    # 도장(Stamp) 찍는 로직 (아직 중간결재 로직 전이라, '승인'이면 둘 다 찍히게 해두었습네다!)
    stamp_dept = ""   # 부서장 도장
    stamp_admin = ""  # 기획실장 도장
    
    # CSS로 만든 빨간 도장 스타일
    stamp_style = "border: 3px solid #cc0000; color: #cc0000; border-radius: 50%; padding: 8px; font-weight: 900; font-size: 16px; transform: rotate(-15deg); display: inline-block;"

    if row['status'] == '승인':
        stamp_dept = f"<div style='{stamp_style}'>승인</div>"
        stamp_admin = f"<div style='{stamp_style}'>승인</div>"
    elif row['status'] == '반려':
        stamp_dept = f"<div style='{stamp_style} border-color: red; color: red;'>반려</div>"
        stamp_admin = ""

    doc_html = f"""
    <div style="border: 2px solid #e0e0e0; padding: 30px; background-color: white; color: black; font-family: 'Malgun Gothic', sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="text-align: center; color: #333; margin-bottom: 30px; letter-spacing: 2px;">휴 가 신 청 서</h2>
        
        <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
            <table style="border-collapse: collapse; text-align: center; border: 1px solid #333; color: black; width: 200px;">
                <tr>
                    <td style="border: 1px solid #333; padding: 5px; background: #f0f0f0; width: 50%; font-size: 13px; font-weight: bold;">부서장</td>
                    <td style="border: 1px solid #333; padding: 5px; background: #f0f0f0; width: 50%; font-size: 13px; font-weight: bold;">기획실장</td>
                </tr>
                <tr style="height: 70px;">
                    <td style="border: 1px solid #333; vertical-align: middle;">{stamp_dept}</td>
                    <td style="border: 1px solid #333; vertical-align: middle;">{stamp_admin}</td>
                </tr>
            </table>
        </div>

        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="border: 1px solid #ddd; background: #f8f9fa; padding: 12px; font-weight: bold; width: 25%; text-align: center;">기안자</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{row['name']}</td>
                <td style="border: 1px solid #ddd; background: #f8f9fa; padding: 12px; font-weight: bold; width: 25%; text-align: center;">신청일</td>
                <td style="border: 1px solid #ddd; padding: 12px;">{row['request_date'][:10]}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; background: #f8f9fa; padding: 12px; font-weight: bold; text-align: center;">휴가 구분</td>
                <td colspan="3" style="border: 1px solid #ddd; padding: 12px;">
                    <span style="background-color: #e3f2fd; color: #1565c0; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{row['vacation_type']}</span>
                </td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; background: #f8f9fa; padding: 12px; font-weight: bold; text-align: center;">사용 기간</td>
                <td colspan="3" style="border: 1px solid #ddd; padding: 12px;">{row['start_date']} ~ {row['end_date']}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; background: #f8f9fa; padding: 12px; font-weight: bold; text-align: center; vertical-align: middle;">사 유</td>
                <td colspan="3" style="border: 1px solid #ddd; padding: 12px; height: 100px; vertical-align: top;">{row['reason']}</td>
            </tr>
        </table>
        <div style="text-align: center; margin-top: 20px; color: #666; font-size: 14px;">
            위와 같이 휴가를 신청하오니 재가 바랍니다.
        </div>
    </div>
    """
    return doc_html

# --- 메인 앱 ---
def main():
    st.set_page_config(page_title="나래병원 전자결재", layout="wide", page_icon="🏥")
    init_db()
    ADMIN_PASSWORD = "1234"

    # CSS
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        .main-header { font-size: 32px; font-weight: 900; color: #1E88E5; text-align: center; margin-top: 10px; margin-bottom: 30px; }
        div[data-testid="stImage"] { display: block; margin-left: auto; margin-right: auto; }
        div.stButton > button { width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    # UI 구성 (로고/제목)
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True) 
        else:
            st.markdown("<h1 style='text-align: center; font-size: 80px;'>🏥</h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-header">나래병원 전자결재시스템</div>', unsafe_allow_html=True)

    st.divider()

    with st.sidebar:
        st.header("사용자 모드")
        user_role = st.selectbox("접속 권한을 선택하세요", ["일반 사원 (신청)", "관리자 (결재)"])
        st.info("💡 나래병원 임직원 전용 시스템입니다.")

    # 1. 일반 사원
    if user_role == "일반 사원 (신청)":
        if 'admin_auth' in st.session_state:
            del st.session_state['admin_auth']

        tab1, tab2 = st.tabs(["📝 휴가 신청", "📊 내 결재 현황"])
        with tab1:
            with st.container(border=True):
                st.subheader("신청서 작성")
                with st.form("request_form", border=False):
                    col1, col2 = st.columns(2)
                    name = col1.text_input("성명")
                    v_type = col2.selectbox("휴가 구분", ["연차", "반차", "병가", "경조사", "대체휴무"])
                    col3, col4 = st.columns(2)
                    s_date = col3.date_input("시작일")
                    e_date = col4.date_input("종료일")
                    reason = st.text_area("신청 사유", height=100)
                    st.write("")
                    submitted = st.form_submit_button("🚀 결재 상신하기", type="primary", use_container_width=True)
                    if submitted:
                        if name and reason:
                            submit_request(name, v_type, s_date, e_date, reason)
                            st.success("✅ 상신되었습니다!")
                        else:
                            st.error("⚠️ 내용을 입력하세요.")

        with tab2:
            st.subheader("📂 나의 문서함")
            search_name = st.text_input("성명 검색", placeholder="이름 입력 후 엔터")
            if search_name:
                my_df = load_data(filter_name=search_name)
                if my_df.empty:
                    st.info("문서가 없습니다.")
                else:
                    for index, row in my_df.iterrows():
                        status_bg = "#f5f5f5"
                        status_color = "#9e9e9e"
                        icon = "⏳"
                        if row['status'] == "승인":
                            status_bg = "#e8f5e9"
                            status_color = "#2e7d32"
                            icon = "✅"
                        elif row['status'] == "반려":
                            status_bg = "#ffebee"
                            status_color = "#c62828"
                            icon = "❌"
                        
                        with st.container(border=True):
                            c1, c2 = st.columns([1, 4])
                            with c1:
                                st.markdown(f"<div style='background-color: {status_bg}; color: {status_color}; border-radius: 8px; padding: 15px; text-align: center; font-weight: bold;'><div>{icon}</div><div>{row['status']}</div></div>", unsafe_allow_html=True)
                            with c2:
                                st.markdown(f"#### [{row['vacation_type']}] {row['name']}")
                                st.caption(f"{row['start_date']} ~ {row['end_date']}")

    # 2. 관리자
    else:
        st.subheader("🔒 관리자 모드")
        if 'admin_auth' not in st.session_state: st.session_state['admin_auth'] = False
        
        if not st.session_state['admin_auth']:
            with st.form("admin_login"):
                if st.form_submit_button("로그인", type="primary", use_container_width=True):
                    if st.text_input("비밀번호", type="password") == ADMIN_PASSWORD: # 폼 안에서 input 받기 수정
                        st.session_state['admin_auth'] = True
                        st.rerun()
                    else: st.error("비밀번호 오류") # *간소화된 로그인 로직*
        else:
            if st.sidebar.button("로그아웃"):
                st.session_state['admin_auth'] = False
                st.rerun()

            tab1, tab2 = st.tabs(["결재 대기 문서", "전체 문서 대장"])
            with tab1:
                pending_df = load_data(filter_status="대기")
                if pending_df.empty: st.success("결재 대기 문서가 없습니다.")
                else:
                    for index, row in pending_df.iterrows():
                        with st.expander(f"📌 {row['name']} - {row['vacation_type']}"):
                            st.markdown(create_document_html(row), unsafe_allow_html=True)
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("✅ 승인", key=f"app_{row['id']}", use_container_width=True):
                                    update_status(row['id'], "승인")
                                    st.rerun()
                            with c2:
                                if st.button("❌ 반려", key=f"rej_{row['id']}", use_container_width=True):
                                    update_status(row['id'], "반려")
                                    st.rerun()
            with tab2:
                st.dataframe(load_data(), use_container_width=True)

if __name__ == '__main__':
    main()