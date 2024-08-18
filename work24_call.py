import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Optional

def get_job_listings(auth_key: str, start_page: int = 1, display: int = 10) -> Optional[pd.DataFrame]:
    base_url = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"
    
    params = {
        "authKey": auth_key,
        "callTp": "L",
        "returnType": "XML",
        "startPage": start_page,
        "display": display
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"API 요청 실패: {e}")
        return None

    root = ET.fromstring(response.content)
    
    # API 응답 전체를 로그로 출력
    st.text("API 응답 내용:")
    st.text(ET.tostring(root, encoding='unicode'))
    
    # 에러 메시지 확인
    error_msg = root.find('.//errorMsg')
    if error_msg is not None:
        st.error(f"API 에러: {error_msg.text}")
        return None
    
    job_data = []
    for item in root.findall('.//wantedInfo'):
        job = {
            "회사": item.findtext('corpInfo/corpNm', default=""),
            "제목": item.findtext('wantedTitle', default=""),
            "급여": item.findtext('salTpNm', default=""),
            "지역": item.findtext('workRegion', default=""),
            "고용형태": item.findtext('empTpNm', default=""),
            "경력": item.findtext('enterTpNm', default=""),
            "학력": item.findtext('eduNm', default="")
        }
        job_data.append(job)
    
    if not job_data:
        st.warning("API에서 반환된 채용 정보가 없습니다.")
        return None
    
    return pd.DataFrame(job_data)

# Streamlit 앱 시작
st.set_page_config(page_title="고용24 채용정보 검색", page_icon="🔍", layout="wide")
st.title("고용24 채용정보 검색")

# 사이드바에 인증키 입력 필드 추가
auth_key = st.sidebar.text_input("인증키를 입력하세요", type="password")

if auth_key:
    # 페이지 번호와 표시 개수 선택
    start_page = st.sidebar.number_input("시작 페이지", min_value=1, value=1)
    display = st.sidebar.number_input("표시 개수", min_value=1, max_value=100, value=10)

    if st.sidebar.button("검색", use_container_width=True):
        with st.spinner("데이터를 불러오는 중..."):
            df = get_job_listings(auth_key, start_page, display)
        
        if df is not None and not df.empty:
            st.success("데이터를 성공적으로 불러왔습니다!")
            st.dataframe(df, use_container_width=True)

            # 데이터 분석 및 시각화
            st.subheader("채용 정보 분석")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 지역별 채용 수
                st.write("지역별 채용 수")
                region_counts = df['지역'].value_counts()
                st.bar_chart(region_counts)

            with col2:
                # 고용형태 분포
                st.write("고용형태 분포")
                emp_type_counts = df['고용형태'].value_counts()
                st.pie_chart(emp_type_counts)

            # CSV 다운로드 버튼
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="CSV로 다운로드",
                data=csv,
                file_name="job_listings.csv",
                mime="text/csv",
            )
        elif df is None:
            st.warning("검색 결과가 없습니다. API 응답을 확인해 주세요.")
else:
    st.info("시작하려면 사이드바에 인증키를 입력하세요.")