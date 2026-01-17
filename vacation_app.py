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
        
    # 날짜(request_date) 기준 내림차순 정렬 (최신순)
    query += " ORDER BY id DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# === HTML 문서 양식 생성 함수 ===
def create_document_html(row):
    doc_html = f"""
<div style="border: 2px solid #333; padding: 20px; background-color: white; color: black; font-family: 'Malgun Gothic', sans-serif;">
    <h1 style="text-align: center; text-decoration: underline; margin-bottom: 30px; color: black;">휴 가 신 청 서</h1>
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
        <table style="border-collapse: collapse; text-align: center; border: 1px solid black; color: black;">
            <tr>
                <td style="border: 1px solid black; padding: 5px; background: #f0f0f0; width: 60px; font-size: 12px;">담당</td>
                <td style="border: 1px solid black; padding: 5px; background: #f0f0f0; width: 60px; font-size: 12px;">팀장</td>
                <td style="border: 1px solid black; padding: 5px; background: #f0f0f0; width: 60px; font-size: 12px;">대표</td>
            </tr>
            <tr style="height: 60px;">
                <td style="border: 1px solid black; vertical-align: middle;">{row['name']}</td>
                <td style="border: 1px solid black;"></td>
                <td style="border: 1px solid black;"></td>
            </tr>
        </table>
    </div>
    <table style="width: 100%; border-collapse: collapse; border: 2px solid black; color: black;">
        <tr>
            <td style="border: 1px solid black; background: #f9f9f9; padding: 10px; font-weight: bold; width: 20%; text-align: center;">성 명</td>
            <td style="border: 1px solid black; padding: 10px;">{row['name']}</td>
            <td style="border: 1px solid black; background: #f9f9f9; padding: 10px; font-weight: bold; width: 20%; text-align: center;">신청일</td>
            <td style="border: 1px solid black; padding: 10px;">{row['request_date'][:10]}</td>
        </tr>
        <tr>
            <td style="border: 1px solid black; background: #f9f9f9; padding: 10px; font-weight: bold; text-align: center;">휴가 종류</td>
            <td colspan="3" style="border: 1px solid black; padding: 10px;">{row['vacation_type']}</td>
        </tr>
        <tr>
            <td style="border: 1px solid black; background: #f9f9f9; padding: 10px; font-weight: bold; text-align: center;">기 간</td>
            <td colspan="3" style="border: 1px solid black; padding: 10px;">
                {row['start_date']} ~ {row['end_date']}
            </td>
        </tr>
        <tr style="height: 150px;">
            <td style="border: 1px solid black; background: #f9f9f9; padding: 10px; font-weight: bold; text-align: center;">사 유</td>
            <td colspan="3" style="border: 1px solid black; padding: 10px; vertical-align: top;">
                {row['reason']}
            </td>
        </tr>
        <tr>
            <td style="border: 1px solid black; background: #f9f9f9; padding: 10px; font-weight: bold; text-align: center;">비상연락망</td>
            <td colspan="3" style="border: 1px solid black; padding: 10px;">
                010-XXXX-XXXX (기본값)
            </td>
        </tr>
    </table>
    <div style="margin-top: 30px; text-align: center; color: black;">
        <p>위와 같이 휴가를 신청하오니 재가 바랍니다.</p>
        <br>
        <h3>신청자 : {row['name']} (인)</h3>
    </div>
</div>
"""
    return doc_html

# --- 메인 앱 ---
def main():
    st.set_page_config(page_title="사내 휴가 결재 시스템", layout="wide")
    init_db()

    # 로고 및 타이틀
    if os.path.exists("logo.png"):
        st.image("logo.png", width=400)
    
    st.title("전자 휴가 결재 시스템")
    if not os.path.exists("logo.png"):
        st.caption("※ logo.png 파일이 폴더에 없어서 로고가 보이지 않습니다.")

    st.divider()

    # 사이드바
    st.sidebar.header("로그인 / 사용자 전환")
    user_role = st.sidebar.selectbox("접속 권한 선택", ["일반 사원 (신청)", "관리자 (결재)"])
    
    # === 1. 일반 사원 화면 ===
    if user_role == "일반 사원 (신청)":
        
        # 탭을 나눠서 기능 분리 (신청 vs 조회)
        tab1, tab2 = st.tabs(["📝 휴가 신청서 작성", "🔎 내 결재 현황 조회"])
        
        # [탭 1] 신청하기
        with tab1:
            st.subheader("새로운 휴가 신청")
            with st.form("request_form"):
                col1, col2 = st.columns(2)
                name = col1.text_input("성명", placeholder="홍길동")
                v_type = col2.selectbox("휴가 종류", ["연차", "반차", "병가", "경조사"])
                col3, col4 = st.columns(2)
                s_date = col3.date_input("시작일")
                e_date = col4.date_input("종료일")
                reason = st.text_area("신청 사유", placeholder="사유를 자세히 입력해주세요")
                
                submitted = st.form_submit_button("결재 올리기")
                if submitted:
                    if name and reason:
                        submit_request(name, v_type, s_date, e_date, reason)
                        st.success(f"✅ {name}님, 휴가 신청이 완료되었습니다! ('내 결재 현황' 탭에서 확인하세요)")
                    else:
                        st.error("⚠️ 성명과 사유를 모두 입력해주세요.")

        # [탭 2] 내 기안 조회하기 (여기가 새로 추가된 부분)
        with tab2:
            st.subheader("🔎 내 기안 문서 진행상황")
            st.info("성명을 입력하고 엔터(Enter)를 치면 내 신청 내역이 조회됩니다.")
            
            search_name = st.text_input("조회할 성명 입력", placeholder="예: 홍길동")
            
            if search_name:
                my_df = load_data(filter_name=search_name)
                
                if my_df.empty:
                    st.warning(f"'{search_name}'님의 신청 내역이 없습니다.")
                else:
                    st.write(f"총 **{len(my_df)}건**의 신청 내역이 있습니다.")
                    st.divider()
                    
                    for index, row in my_df.iterrows():
                        # 상태에 따른 색상 및 아이콘 설정
                        status_color = "gray"
                        icon = "⏳"
                        if row['status'] == "승인":
                            status_color = "green"
                            icon = "✅"
                        elif row['status'] == "반려":
                            status_color = "red"
                            icon = "❌"
                        elif row['status'] == "대기":
                            status_color = "orange"
                            icon = "⏳"

                        # 카드 형태로 보여주기
                        with st.container():
                            c1, c2 = st.columns([1, 4])
                            with c1:
                                # 상태 표시 (큰 글씨)
                                st.markdown(f"""
                                    <div style='text-align: center; border: 2px solid {status_color}; border-radius: 10px; padding: 10px; color: {status_color}; font-weight: bold;'>
                                        <div style='font-size: 24px;'>{icon}</div>
                                        <div>{row['status']}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                            with c2:
                                st.markdown(f"**[{row['vacation_type']}] {row['start_date']} ~ {row['end_date']}**")
                                st.caption(f"신청일: {row['request_date'][:16]}")
                                st.write(f"사유: {row['reason']}")
                            st.divider()

    # === 2. 관리자 화면 ===
    else:
        st.subheader("master 관리자 모드")
        tab1, tab2 = st.tabs(["결재 대기 문서", "전체 기록 조회"])
        
        with tab1:
            st.write("🔴 **승인 대기 중인 문서**")
            pending_df = load_data(filter_status="대기")
            
            if pending_df.empty:
                st.info("현재 대기 중인 결재 문서가 없습니다.")
            else:
                for index, row in pending_df.iterrows():
                    # 버튼 제목
                    btn_label = f"📄 [{row['vacation_type']}] {row['name']} - {row['start_date']} (문서 확인하기)"
                    
                    with st.expander(btn_label):
                        # === 문서 양식 보여주기 ===
                        html_code = create_document_html(row)
                        st.markdown(html_code, unsafe_allow_html=True)
                        
                        st.write("") # 여백
                        
                        # 승인/반려 버튼
                        c1, c2, c3 = st.columns([1, 1, 3])
                        with c1:
                            if st.button("✅ 승인", key=f"approve_{row['id']}"):
                                update_status(row['id'], "승인")
                                st.rerun()
                        with c2:
                            if st.button("❌ 반려", key=f"reject_{row['id']}"):
                                update_status(row['id'], "반려")
                                st.rerun()
        
        with tab2:
            st.write("📊 **전체 휴가 신청 내역**")
            all_df = load_data()
            st.dataframe(all_df)

if __name__ == '__main__':
    main()