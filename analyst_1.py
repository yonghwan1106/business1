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
- 최근 5년간의 연도별 시장 성장률 제시
- 현재 국내 및 글로벌 시장 규모 (금액으로 표시)
- 주요 소비자 트렌드 3-5가지 나열 및 각각에 대한 간단한 설명
- 시장을 주도하는 핵심 기술이나 혁신 요소 설명

## 2. 경쟁 상황 평가
- 국내외 주요 경쟁사 3-5개 식별 및 각 기업의 강점과 약점 분석
- 시장 점유율 상위 3개 기업의 점유율 수치 제시
- 신규 진입자가 직면할 수 있는 주요 진입 장벽 3-5가지 나열 및 설명
- 대체 상품/서비스의 위협 정도 평가

## 3. 성장 전망 예측
- AI 기반으로 향후 3년, 5년간의 예상 시장 성장률 제시
- 낙관적, 중립적, 비관적 시나리오별 성장 전망 및 각 시나리오의 주요 가정 설명
- 시장 성장에 영향을 미칠 수 있는 주요 외부 요인(정책, 기술 발전 등) 분석

## 4. 성공 사례 분석
- 해당 분야에서 성공한 국내외 기업 2-3개 사례 제시
- 각 성공 사례의 주요 성공 요인 3-5가지 분석
- 성공 기업들의 초기 진입 전략과 성장 과정에서의 주요 전환점 설명
- 경쟁사와의 차별화 포인트 상세 분석

## 5. 실패 사례 분석
- 해당 분야에서 실패한 국내외 기업 2-3개 사례 제시
- 각 실패 사례의 주요 실패 원인 3-5가지 분석
- 실패를 극복하기 위한 구체적인 방안 제시
- 각 실패 사례에서 얻을 수 있는 핵심 교훈 도출

## 6. 핵심 성공 요인 도출
- 데이터 마이닝을 통해 식별된 해당 아이템의 핵심 성공 요인 5-7가지 나열
- 각 성공 요인의 중요도를 1-10 척도로 평가 및 그 이유 설명
- 제시된 창업 아이템의 각 성공 요인에 대한 적합성 평가 및 개선 방안 제시
- 아이템의 장기적 성공을 위한 전략적 제언 3-5가지 제공

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