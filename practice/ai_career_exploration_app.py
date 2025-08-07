
import streamlit as st
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 상태 정의
class CareerState(TypedDict):
    step_state: Annotated[str, "단계 상태"]
    is_react: Annotated[bool, "React 여부, 기본값은 False, 재실행 요청시 True"]
    career: Annotated[str, "학생이 선택한 직업"]
    career_values: Annotated[list[str], "직업에 대한 가치관, 다중 선택 가능"]
    career_issues: Annotated[list[str], "직업에 대한 이슈, 다중 선택 가능"]
    career_issues_generated: Annotated[list[list[str]], "LLM으로 생성된 이슈 목록들"]
    career_issues_count: Annotated[int, "이슈 생성 횟수 (최대 5회)"]
    career_exploration: Annotated[str, "직업 탐구주제"]
    career_final_goal: Annotated[str, "직업 탐구 최종 목표"]
    career_middle_goal: Annotated[list[str], "직업 탐구 중간 목표"]
    career_final_report: Annotated[str, "직업 탐구 최종 보고서"]
    messages: Annotated[list, add_messages]

def web_select_career(state: CareerState) -> CareerState:
    """웹에서 직업 선택 함수"""
    st.header("1단계: 직업 선택")

    career_input = st.text_input(
        "원하는 직업을 입력해주세요:",
        placeholder="예: 건축가, 소프트웨어 개발자, AI 엔지니어, 의사, 교사...",
        key="career_input"
    )

    if st.button("다음 단계로", key="career_submit"):
        if career_input.strip():
            new_state = {
                **state,
                "step_state": "2",
                "career": career_input.strip(),
                "is_react": False,
                "messages": state.get("messages", []) + [f"직업을 선택했습니다: {career_input.strip()}"]
            }
            st.session_state.career_state = new_state
            st.success(f"✅ 선택한 직업: {career_input.strip()}")
            st.rerun()
            return new_state
        else:
            st.error("직업을 입력해주세요!")
    return state

def web_select_career_values(state: CareerState) -> CareerState:
    """웹에서 직업 가치관 선택 함수 - 6가지 선택지"""
    st.header("2단계: 직업 가치관 선택")
    st.write(f"선택한 직업: **{state.get('career', '')}**")

    value_options = [
        "1. 경제적 가치 - 높은 수입, 안정적인 직업",
        "2. 사회적 가치 - 사회에 긍정적인 영향, 봉사", 
        "3. 공동체적 가치 - 사람들과 협력, 소통",
        "4. 능력 발휘 - 나의 재능과 역량을 최대한 발휘",
        "5. 자율·창의성 - 독립적으로 일하고 새로운 아이디어 창출",
        "6. 미래 비전 - 성장 가능성, 혁신적인 분야"
    ]

    selected_values = st.multiselect(
        "직업을 선택한 이유/가치관을 모두 선택하세요:",
        value_options,
        key="career_values_input"
    )

    if st.button("다음 단계로", key="values_submit"):
        if selected_values:
            new_state = {
                **state,
                "step_state": "3",
                "career_values": selected_values,
                "is_react": False,
                "messages": state.get("messages", []) + [f"직업 가치관을 선택했습니다: {', '.join(selected_values)}"]
            }
            st.session_state.career_state = new_state
            st.success(f"✅ 선택한 가치관: {', '.join(selected_values)}")
            st.rerun()
            return new_state
        else:
            st.error("최소 하나의 가치관을 선택해주세요!")
    return state

def generate_career_issues_with_llm(career: str, career_values: list, previous_issues: list = None) -> list:
    """LLM을 사용하여 직업 이슈 생성"""
    if previous_issues is None:
        previous_issues = []

    # 이전에 생성된 모든 이슈들을 평탄화
    all_previous_issues = []
    for issues_list in previous_issues:
        all_previous_issues.extend(issues_list)

    prompt = f"""
당신은 진로 상담 전문가입니다. 다음 조건에 맞는 직업 분야의 최신 이슈나 해결 과제 5가지를 제시해주세요.

**직업**: {career}
**가치관**: {', '.join(career_values)}

**요구사항**:
1. 해당 직업 분야의 최신 이슈나 최근 문제가 되고 있는 해결 과제 5가지
2. 선택된 가치관({', '.join(career_values)})을 고려한 이슈들
3. 구체적이고 현실적인 문제들
4. 각 이슈는 한 줄로 간결하게 표현

**중복 방지**: 다음 이슈들과는 다른 새로운 이슈를 제시해주세요:
{', '.join(all_previous_issues) if all_previous_issues else '없음'}

**응답 형식**: 
- 이슈1
- 이슈2  
- 이슈3
- 이슈4
- 이슈5
"""

    try:
        response = llm.invoke(prompt)
        generated_text = response.content

        # 응답에서 이슈 추출
        issues = []
        for line in generated_text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                # '-' 또는 '•' 제거하고 이슈 추출
                issue = line[1:].strip()
                if issue and len(issue) > 5:  # 최소 길이 확인
                    issues.append(issue)

        # 5개가 아닌 경우 조정
        if len(issues) < 5:
            issues.extend([f"{career} 분야의 추가 과제 {i+1}" for i in range(len(issues), 5)])
        elif len(issues) > 5:
            issues = issues[:5]

        return issues

    except Exception as e:
        st.error(f"이슈 생성 중 오류가 발생했습니다: {e}")
        # 실패 시 기본 이슈 반환
        return [
            f"{career} 분야의 경쟁력 강화 필요",
            "기술 변화에 대한 적응 과제",
            "전문성 개발 요구 증가",
            "워라밸 개선 필요",
            "미래 시장 변화 대응 과제"
        ]

def web_select_career_issues(state: CareerState) -> CareerState:
    """웹에서 직업 이슈 선택 함수 - LLM 기반 동적 생성"""
    st.header("3단계: 직업 관련 이슈 선택 (AI 기반)")
    st.write(f"**선택한 직업:** {state.get('career', '')}")
    st.write(f"**선택한 가치관:** {', '.join(state.get('career_values', []))}")

    career_issues_count = state.get('career_issues_count', 0)
    career_issues_generated = state.get('career_issues_generated', [])

    # 이슈 생성 상태 표시
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"🤖 AI가 {state.get('career', '')} 직업의 최신 이슈를 분석 중...")
    with col2:
        st.metric("생성 횟수", f"{career_issues_count}/5")

    # 첫 실행이거나 재실행인 경우 이슈 생성
    if career_issues_count == 0 or state.get('generate_new', False):
        if career_issues_count < 5:
            with st.spinner("AI가 직업 이슈를 생성하고 있습니다..."):
                new_issues = generate_career_issues_with_llm(
                    state.get('career', ''),
                    state.get('career_values', []),
                    career_issues_generated
                )

            # 새 이슈를 상태에 저장
            new_career_issues_generated = career_issues_generated + [new_issues]
            new_career_issues_count = career_issues_count + 1

            new_state = {
                **state,
                "career_issues": new_issues,
                "career_issues_generated": new_career_issues_generated,
                "career_issues_count": new_career_issues_count,
                "generate_new": False
            }
            st.session_state.career_state = new_state
            state = new_state

    # 현재 이슈 표시
    current_issues = state.get('career_issues', [])
    if current_issues:
        st.subheader("🔍 AI가 분석한 주요 이슈들")
        for i, issue in enumerate(current_issues, 1):
            st.write(f"**{i}.** {issue}")

    # 버튼들
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 다른 이슈 보기", key="regenerate_issues"):
            if career_issues_count < 5:
                new_state = {
                    **state,
                    "generate_new": True
                }
                st.session_state.career_state = new_state
                st.rerun()
            else:
                st.warning("최대 생성 횟수(5회)에 도달했습니다.")

    with col2:
        if st.button("📋 이전 이슈 보기", key="show_history"):
            if career_issues_generated:
                st.subheader("📚 이전에 생성된 이슈들")
                for i, issues in enumerate(career_issues_generated, 1):
                    with st.expander(f"{i}번째 생성 ({len(issues)}개)"):
                        for j, issue in enumerate(issues, 1):
                            st.write(f"{j}. {issue}")

    with col3:
        if st.button("다음 단계로", key="issues_submit"):
            if current_issues:
                new_state = {
                    **state,
                    "step_state": "4",
                    "is_react": False,
                    "messages": state.get("messages", []) + [f"AI가 생성한 직업 이슈를 확인했습니다 ({career_issues_count}/5회 생성)"]
                }
                st.session_state.career_state = new_state
                st.success("✅ 직업 이슈 분석이 완료되었습니다!")
                st.rerun()
                return new_state
            else:
                st.error("이슈가 생성되지 않았습니다. 다시 시도해주세요.")

    return state

# 나머지 함수들은 이전과 동일...
def web_select_career_exploration(state: CareerState) -> CareerState:
    """웹에서 직업 탐구 주제 선택 함수"""
    st.header("4단계: 직업 탐구 주제 설정")
    st.write(f"선택한 직업: **{state.get('career', '')}**")

    exploration_input = st.text_area(
        "직업 탐구 주제를 입력해주세요:",
        placeholder="예: AI 개발자의 미래 전망과 필요 역량 분석",
        height=100,
        key="career_exploration_input"
    )

    if st.button("다음 단계로", key="exploration_submit"):
        if exploration_input.strip():
            new_state = {
                **state,
                "step_state": "5",
                "career_exploration": exploration_input.strip(),
                "is_react": False,
                "messages": state.get("messages", []) + [f"직업 탐구 주제를 설정했습니다: {exploration_input.strip()}"]
            }
            st.session_state.career_state = new_state
            st.success(f"✅ 탐구 주제: {exploration_input.strip()}")
            st.rerun()
            return new_state
        else:
            st.error("탐구 주제를 입력해주세요!")
    return state

def main():
    """메인 Streamlit 웹 앱"""
    st.set_page_config(
        page_title="AI 진로 탐구 시스템",
        page_icon="🎯",
        layout="wide"
    )

    st.title("🎯 AI 진로 탐구 시스템")
    st.markdown("**AI와 함께하는 체계적인 진로 탐구** - 나만의 커리어 로드맵을 만들어보세요!")

    # 세션 상태 초기화
    if 'career_state' not in st.session_state:
        st.session_state.career_state = {
            "step_state": "1",
            "is_react": False,
            "career": "",
            "career_values": [],
            "career_issues": [],
            "career_issues_generated": [],
            "career_issues_count": 0,
            "career_exploration": "",
            "career_final_goal": "",
            "career_middle_goal": [],
            "career_final_report": "",
            "messages": ["AI 진로 탐구를 시작합니다."],
            "generate_new": False
        }

    # 현재 단계
    current_step = st.session_state.career_state.get("step_state", "1")

    # 진행 상황 표시
    step_names = {
        "1": "직업 선택", "2": "가치관 선택", "3": "AI 이슈 분석",
        "4": "탐구 주제", "5": "최종 목표", "6": "중간 목표", "7": "최종 보고서"
    }

    st.subheader(f"📍 현재 단계: {step_names.get(current_step, '완료')}")

    # 진행 바
    if current_step.isdigit():
        progress_value = int(current_step) / 7
        st.progress(progress_value)

    # 사이드바
    with st.sidebar:
        st.header("📊 진행 상황")
        for step, name in step_names.items():
            icon = "✅" if current_step.isdigit() and int(current_step) > int(step) else "🔄" if current_step == step else "⏳"
            st.write(f"{icon} {step}단계: {name}")

        # AI 이슈 생성 상태 표시
        if current_step == "3":
            issues_count = st.session_state.career_state.get('career_issues_count', 0)
            st.info(f"🤖 AI 이슈 생성: {issues_count}/5회")

        if st.button("🔄 처음부터 다시 시작"):
            st.session_state.clear()
            st.rerun()

    # 단계별 함수 실행
    step_functions = {
        "1": web_select_career,
        "2": web_select_career_values,
        "3": web_select_career_issues,
        "4": web_select_career_exploration
        # 나머지 단계들은 필요에 따라 추가
    }

    if current_step in step_functions:
        step_functions[current_step](st.session_state.career_state)
    elif current_step == "completed":
        st.success("🎉 모든 단계가 완료되었습니다!")
        st.write("AI와 함께한 진로 탐구를 성공적으로 마쳤습니다. 수고하셨습니다!")

if __name__ == "__main__":
    main()
