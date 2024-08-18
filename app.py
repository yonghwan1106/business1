import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from typing import Optional, Tuple

# 인증키를 직접 코드에 삽입
AUTH_KEY = "b2f7660c-9fd4-4525-9d2e-6cd14440ec35"  # 여기에 실제 인증키를 입력하세요

def get_job_listings(start_page: int = 1, display: int = 10) -> Tuple[Optional[pd.DataFrame], str]:
    base_url = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"
    
    params = {
        "authKey": AUTH_KEY,
        "callTp": "L",
        "returnType": "XML",
        "startPage": start_page,
        "display": display
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        return None, f"API 요청 실패: {e}"

    root = ET.fromstring(response.content)
    
    # 에러 메시지 확인
    error_elem = root.find('.//error')
    if error_elem is not None:
        return None, f"API 에러: {error_elem.text}"
    
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
        return None, "API에서 반환된 채용 정보가 없습니다."
    
    return pd.DataFrame(job_data), "성공"

# Streamlit 앱 시작
st.set_page_config(page_title="고용24 채용정보 검색", page_icon="🔍", layout="wide")
st.title("고용24 채용정보 검색")

# 페이지 번호와 표시 개수 선택
start_page = st.sidebar.number_input("시작 페이지", min_value=1, value=1)
display = st.sidebar.number_input("표시 개수", min_value=1, max_value=100, value=10)

if st.sidebar.button("검색", use_container_width=True):
    with st.spinner("데이터를 불러오는 중..."):
        df, message = get_job_listings(start_page, display)
    
    if df is not None:
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
    else:
        st.error(f"검색 결과가 없습니다. 원인: {message}")
        st.info("API 키를 확인하고 고용24 사이트에서 서비스 신청 상태를 확인해주세요.")

# API 응답 전체를 로그로 출력 (디버깅 목적)
if st.checkbox("API 응답 내용 보기"):
    st.text(f"API 응답 내용:\n{message}")