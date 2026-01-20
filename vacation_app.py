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

# === HTML 문서 양식 (관리자용) ===
def create_document_html(row):
    doc_html = f"""
    <div style="border: 2px solid #e0e0e0; padding: 30px; background-color: white; color: black; font-family: 'Malgun Gothic', sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="text-align: center; color: #333; margin-bottom: 30px; letter-spacing: 2px;">휴 가 신 청 서</h2>
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
    st.set_page_config(page_title="Smart 휴가결재", layout="wide", page_icon="🏢")
    init_db()

    # 관리자 비밀번호
    ADMIN_PASSWORD = "1234"

    # === [스타일] 커스텀 CSS (더 깔끔하게) ===
    st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
        }
        .main-header {
            font-size: 24px; 
            font-weight: bold; 
            color: #1E88E5;
            margin-bottom: 20px;
        }
        .card-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # 로고와 헤더 (깔끔한 배치)
    col1, col2 = st.columns([1, 6])
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=80)
        else:
            st.write("🏢") # 로고 없으면 아이콘
    with col2:
        st.markdown('<div class="main-header">Smart 전자 결재 시스템</div>', unsafe_allow_html=True)

    st.divider()

    # 사이드바
    with st.sidebar:
        st.header("사용자 모드")
        user_role = st.selectbox("접속 권한을 선택하세요", ["일반 사원 (신청)", "관리자 (결재)"])
        st.info("💡 쾌적한 업무 환경을 지원합니다.")

    # === 1. 일반 사원 화면 ===
    if user_role == "일반 사원 (신청)":
        if 'admin_auth' in st.session_state:
            del st.session_state['admin_auth']

        tab1, tab2 = st.tabs(["📝 휴가 신청", "📊 내 결재 현황"])
        
        with tab1:
            st.markdown("#### 👋 안녕하세요! 휴가 계획이 있으신가요?")
            
            # 대시보드 느낌의 카드 (가짜 데이터지만 실제처럼 보임)
            with st.container():
                c1, c2, c3 = st.columns(3)
                c1.metric(label="총 연차", value="15일")
                c2.metric(label="사용 연차", value="3일")
                c3.metric(label="잔여 연차", value="12일", delta="-1일 (예정)")
            
            st.write("") # 여백
            
            # 신청 폼 (박스로 감싸서 깔끔하게)
            with st.container(border=True):
                st.subheader("신청서 작성")
                with st.form("request_form", border=False):
                    col1, col2 = st.columns(2)
                    name = col1.text_input("성명", placeholder="이름을 입력하세요")
                    v_type = col2.selectbox("휴가 구분", ["연차", "반차", "병가", "경조사", "대체휴무"])
                    
                    col3, col4 = st.columns(2)
                    s_date = col3.date_input("시작일")
                    e_date = col4.date_input("종료일")
                    
                    reason = st.text_area("신청 사유", placeholder="업무 공유 사항 및 비상 연락망 등을 기재해 주세요.", height=100)
                    
                    st.write("")
                    submitted = st.form_submit_button("🚀 결재 상신하기", type="primary", use_container_width=True)
                    
                    if submitted:
                        if name and reason:
                            submit_request(name, v_type, s_date, e_date, reason)
                            st.success("✅ 상신되었습니다! 결재 진행 상황은 '내 결재 현황' 탭에서 확인하세요.")
                        else:
                            st.error("⚠️ 성명과 사유를 정확히 입력해 주세요.")

        with tab2:
            st.subheader("📂 나의 문서함")
            search_name = st.text_input("성명 검색", placeholder="본인 이름을 입력하고 엔터를 누르세요")
            
            if search_name:
                my_df = load_data(filter_name=search_name)
                
                if my_df.empty:
                    st.info(f"📭 '{search_name}'님의 문서 내역이 없습니다.")
                else:
                    st.success(f"총 {len(my_df)}건의 문서가 조회되었습니다.")
                    for index, row in my_df.iterrows():
                        # 디자인된 상태 카드
                        status_color = "#9e9e9e" # 회색 (기본)
                        status_bg = "#f5f5f5"
                        icon = "⏳"
                        
                        if row['status'] == "승인":
                            status_color = "#2e7d32" # 초록
                            status_bg = "#e8f5e9"
                            icon = "✅"
                        elif row['status'] == "반려":
                            status_color = "#c62828" # 빨강
                            status_bg = "#ffebee"
                            icon = "❌"
                        elif row['status'] == "대기":
                            status_color = "#ff9800" # 주황
                            status_bg = "#fff3e0"
                            icon = "⏳"

                        with st.container(border=True):
                            c1, c2 = st.columns([1, 4])
                            with c1:
                                st.markdown(f"""
                                    <div style='
                                        background-color: {status_bg}; 
                                        color: {status_color}; 
                                        border-radius: 8px; 
                                        padding: 15px; 
                                        text-align: center;
                                        font-weight: bold;
                                        height: 100%;
                                        display: flex; flex-direction: column; justify-content: center;
                                    '>
                                        <div style='font-size: 20px; margin-bottom: 5px;'>{icon}</div>
                                        <div>{row['status']}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            with c2:
                                st.markdown(f"#### [{row['vacation_type']}] {row['start_date']} ~ {row['end_date']}")
                                st.caption(f"기안일: {row['request_date'][:16]}")
                                st.write(f"**사유:** {row['reason']}")

    # === 2. 관리자 화면 ===
    else:
        st.subheader("🔒 관리자 모드")
        
        if 'admin_auth' not in st.session_state:
            st.session_state['admin_auth'] = False

        if not st.session_state['admin_auth']:
            with st.form("admin_login"):
                password_input = st.text_input("비밀번호", type="password")
                login_btn = st.form_submit_button("로그인", type="primary")
                if login_btn:
                    if password_input == ADMIN_PASSWORD:
                        st.session_state['admin_auth'] = True
                        st.rerun()
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
        
        else:
            if st.sidebar.button("로그아웃"):
                st.session_state['admin_auth'] = False
                st.rerun()

            tab1, tab2 = st.tabs(["결재 대기 문서", "전체 문서 대장"])
            
            with tab1:
                pending_df = load_data(filter_status="대기")
                
                if pending_df.empty:
                    st.balloons()
                    st.success("모든 결재 처리가 완료되었습니다! 🎉")
                else:
                    st.write(f"🔴 **{len(pending_df)}건**의 미결재 문서가 있습니다.")
                    for index, row in pending_df.iterrows():
                        with st.expander(f"📌 [{row['name']}] {row['vacation_type']} 신청건 ({row['start_date']})"):
                            # 디자인된 문서 양식 출력
                            st.markdown(create_document_html(row), unsafe_allow_html=True)
                            
                            st.write("")
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.button("✅ 승인 처리", key=f"approve_{row['id']}", type="primary", use_container_width=True):
                                    update_status(row['id'], "승인")
                                    st.rerun()
                            with c2:
                                if st.button("❌ 반려 처리", key=f"reject_{row['id']}", use_container_width=True):
                                    update_status(row['id'], "반려")
                                    st.rerun()
            
            with tab2:
                st.markdown("#### 📊 전체 휴가 사용 내역")
                all_df = load_data()
                st.dataframe(all_df, use_container_width=True)

if __name__ == '__main__':
    main()