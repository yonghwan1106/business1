import streamlit as st
import anthropic

# Streamlit 앱 설정
st.set_page_config(page_title="스타트업 내비게이터", page_icon="🚀", layout="wide")

# 세션 상태 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

# API 키 입력 섹션
st.sidebar.header("API 키 설정")
api_key_input = st.sidebar.text_input("Anthropic API 키를 입력하세요:", type="password")
if st.sidebar.button("API 키 저장"):
    st.session_state.api_key = api_key_input
    st.sidebar.success("API 키가 저장되었습니다!")

def analyze_startup_idea(idea, api_key):
    prompt = f"""다음 창업 아이디어에 대해 상세한 분석을 제공해주세요: {idea}

    분석은 다음 구조를 따라야 합니다:

    ## 1. 시장 동향 분석
    ...

    각 섹션에 대해 상세하고 구체적인 정보를 제공해 주세요."""

    try:
        st.info(f"API 키 길이: {len(api_key)}")  # API 키 길이 출력 (보안상 전체 키는 출력하지 않음)
        claude = anthropic.Client(api_key=api_key)
        st.info("Claude 클라이언트 생성 성공")
        response = claude.completions.create(
            model="claude-3-sonnet-20240229",
            prompt=prompt,
            max_tokens_to_sample=4000,
        )
        st.info("API 요청 성공")
        return response.completion
    except anthropic.AuthenticationError as e:
        st.error(f"API 키 인증에 실패했습니다. 오류 메시지: {str(e)}")
        return None
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        return None

# Streamlit UI
st.title("🚀 스타트업 내비게이터")

st.header("창업 아이템 분석기")
idea = st.text_area("당신의 창업 아이디어를 입력하세요:")

if st.button("분석하기"):
    if not st.session_state.api_key:
        st.warning("API 키를 먼저 입력해주세요.")
    elif not idea:
        st.warning("아이디어를 입력해주세요.")
    else:
        st.info("분석을 시작합니다...")
        analysis = analyze_startup_idea(idea, st.session_state.api_key)
        if analysis:
            st.markdown(analysis)

# 추가 기능은 여기에 구현할 수 있습니다.