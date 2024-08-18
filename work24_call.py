import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

def get_job_listings(auth_key, start_page=1, display=10):
    base_url = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"
    
    params = {
        "authKey": auth_key,
        "callTp": "L",
        "returnType": "XML",
        "startPage": start_page,
        "display": display
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        
        job_data = []
        for item in root.findall('.//wantedInfo'):
            job = {
                "회사": item.find('corpInfo/corpNm').text,
                "제목": item.find('wantedTitle').text,
                "급여": item.find('salTpNm').text,
                "지역": item.find('workRegion').text,
                "고용형태": item.find('empTpNm').text,
                "경력": item.find('enterTpNm').text,
                "학력": item.find('eduNm').text
            }
            job_data.append(job)
        
        return pd.DataFrame(job_data)
    else:
        st.error(f"API 호출 실패: {response.status_code}")
        return None

# Streamlit 앱 시작
st.title("고용24 채용정보 검색")

# 사이드바에 인증키 입력 필드 추가
auth_key = st.sidebar.text_input("인증키를 입력하세요", type="password")

if auth_key:
    # 페이지 번호와 표시 개수 선택
    start_page = st.sidebar.number_input("시작 페이지", min_value=1, value=1)
    display = st.sidebar.number_input("표시 개수", min_value=1, max_value=100, value=10)

    if st.sidebar.button("검색"):
        with st.spinner("데이터를 불러오는 중..."):
            df = get_job_listings(auth_key, start_page, display)
        
        if df is not None and not df.empty:
            st.success("데이터를 성공적으로 불러왔습니다!")
            st.dataframe(df)

            # 데이터 분석 및 시각화
            st.subheader("채용 정보 분석")
            
            # 지역별 채용 수
            st.write("지역별 채용 수")
            region_counts = df['지역'].value_counts()
            st.bar_chart(region_counts)

            # 고용형태 분포
            st.write("고용형태 분포")
            emp_type_counts = df['고용형태'].value_counts()
            st.pie_chart(emp_type_counts)

            # CSV 다운로드 버튼
            csv = df.to_csv(index=False)
            st.download_button(
                label="CSV로 다운로드",
                data=csv,
                file_name="job_listings.csv",
                mime="text/csv",
            )
        elif df is not None:
            st.warning("검색 결과가 없습니다.")
else:
    st.info("시작하려면 사이드바에 인증키를 입력하세요.")