
import streamlit as st
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 상태 정의
class CareerState(TypedDict):
    step_state: Annotated[str, "단계 상태"]
    is_react: Annotated[bool, "React 여부, 기본값은 False, 재실행 요청시 True"]
    career: Annotated[str, "학생이 선택한 직업"]
    career_values: Annotated[list[str], "직업에 대한 가치관, 다중 선택 가능"]
    career_issues: Annotated[list[str], "직업에 대한 이슈, 다중 선택 가능"]
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
        placeholder="예: 소프트웨어 개발자, AI 엔지니어, 데이터 사이언티스트...",
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

def web_select_career_issues(state: CareerState) -> CareerState:
    """웹에서 직업 이슈 선택 함수"""
    st.header("3단계: 직업 관련 이슈 선택")
    st.write(f"선택한 직업: **{state.get('career', '')}**")

    issue_options = [
        "치열한 경쟁", "기술 변화 속도", "불안정한 고용", "높은 스트레스",
        "워라밸 부족", "낮은 초봉", "진입장벽", "업무 과부하",
        "인간관계", "승진 어려움"
    ]

    selected_issues = st.multiselect(
        "해당 직업의 주요 이슈나 걱정되는 점을 모두 선택하세요:",
        issue_options,
        key="career_issues_input"
    )

    if st.button("다음 단계로", key="issues_submit"):
        if selected_issues:
            new_state = {
                **state,
                "step_state": "4",
                "career_issues": selected_issues,
                "is_react": False,
                "messages": state.get("messages", []) + [f"직업 이슈를 선택했습니다: {', '.join(selected_issues)}"]
            }
            st.session_state.career_state = new_state
            st.success(f"✅ 선택한 이슈: {', '.join(selected_issues)}")
            st.rerun()
            return new_state
        else:
            st.error("최소 하나의 이슈를 선택해주세요!")
    return state

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

def web_select_career_final_goal(state: CareerState) -> CareerState:
    """웹에서 직업 탐구 최종 목표 설정 함수"""
    st.header("5단계: 직업 탐구 최종 목표")
    st.write(f"탐구 주제: **{state.get('career_exploration', '')}**")

    final_goal_input = st.text_area(
        "직업 탐구를 통해 달성하고자 하는 최종 목표를 입력해주세요:",
        placeholder="예: 3년 내 AI 전문가로 성장하기",
        height=100,
        key="career_final_goal_input"
    )

    if st.button("다음 단계로", key="final_goal_submit"):
        if final_goal_input.strip():
            new_state = {
                **state,
                "step_state": "6",
                "career_final_goal": final_goal_input.strip(),
                "is_react": False,
                "messages": state.get("messages", []) + [f"최종 목표를 설정했습니다: {final_goal_input.strip()}"]
            }
            st.session_state.career_state = new_state
            st.success(f"✅ 최종 목표: {final_goal_input.strip()}")
            st.rerun()
            return new_state
        else:
            st.error("최종 목표를 입력해주세요!")
    return state

def web_select_career_middle_goal(state: CareerState) -> CareerState:
    """웹에서 직업 탐구 중간 목표 설정 함수"""
    st.header("6단계: 중간 목표 설정")
    st.write(f"최종 목표: **{state.get('career_final_goal', '')}**")

    if 'middle_goals' not in st.session_state:
        st.session_state.middle_goals = ['']

    middle_goals = []
    for i, goal in enumerate(st.session_state.middle_goals):
        goal_input = st.text_input(
            f"중간 목표 {i+1}:",
            value=goal,
            placeholder="예: Python 마스터하기",
            key=f"middle_goal_{i}"
        )
        if goal_input.strip():
            middle_goals.append(goal_input.strip())

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ 중간 목표 추가", key="add_middle_goal"):
            st.session_state.middle_goals.append('')
            st.rerun()
    with col2:
        if st.button("➖ 마지막 목표 제거", key="remove_middle_goal"):
            if len(st.session_state.middle_goals) > 1:
                st.session_state.middle_goals.pop()
                st.rerun()

    if st.button("다음 단계로", key="middle_goals_submit"):
        if middle_goals:
            new_state = {
                **state,
                "step_state": "7",
                "career_middle_goal": middle_goals,
                "is_react": False,
                "messages": state.get("messages", []) + [f"중간 목표를 설정했습니다: {', '.join(middle_goals)}"]
            }
            st.session_state.career_state = new_state
            st.success(f"✅ 중간 목표: {', '.join(middle_goals)}")
            st.rerun()
            return new_state
        else:
            st.error("최소 하나의 중간 목표를 입력해주세요!")
    return state

def web_select_career_final_report(state: CareerState) -> CareerState:
    """웹에서 직업 탐구 최종 보고서 작성 함수"""
    st.header("7단계: 직업 탐구 최종 보고서")

    st.subheader("📋 탐구 정보 요약")
    st.write(f"**직업:** {state.get('career', '')}")
    st.write(f"**가치관:** {', '.join(state.get('career_values', []))}")
    st.write(f"**이슈:** {', '.join(state.get('career_issues', []))}")
    st.write(f"**탐구 주제:** {state.get('career_exploration', '')}")
    st.write(f"**최종 목표:** {state.get('career_final_goal', '')}")
    st.write(f"**중간 목표:** {', '.join(state.get('career_middle_goal', []))}")

    st.subheader("📝 최종 보고서 작성")
    report_input = st.text_area(
        "위 정보를 바탕으로 직업 탐구 보고서를 작성해주세요:",
        placeholder="탐구 과정에서 배운 점, 느낀 점, 앞으로의 계획 등을 포함하여 보고서를 작성해주세요.",
        height=200,
        key="career_final_report_input"
    )

    if st.button("보고서 완성", key="final_report_submit"):
        if report_input.strip():
            new_state = {
                **state,
                "step_state": "completed",
                "career_final_report": report_input.strip(),
                "is_react": False,
                "messages": state.get("messages", []) + ["최종 보고서를 작성했습니다."]
            }
            st.session_state.career_state = new_state
            st.success("✅ 진로 탐구가 완료되었습니다!")
            st.balloons()
            st.subheader("🎉 진로 탐구 완료!")
            return new_state
        else:
            st.error("보고서를 작성해주세요!")
    return state

def main():
    """메인 Streamlit 웹 앱"""
    st.set_page_config(
        page_title="진로 탐구 시스템",
        page_icon="🎯",
        layout="wide"
    )

    st.title("🎯 진로 탐구 시스템")
    st.markdown("체계적인 진로 탐구를 통해 나만의 커리어 로드맵을 만들어보세요!")

    # 세션 상태 초기화
    if 'career_state' not in st.session_state:
        st.session_state.career_state = {
            "step_state": "1",
            "is_react": False,
            "career": "",
            "career_values": [],
            "career_issues": [],
            "career_exploration": "",
            "career_final_goal": "",
            "career_middle_goal": [],
            "career_final_report": "",
            "messages": ["진로 탐구를 시작합니다."]
        }

    # 현재 단계
    current_step = st.session_state.career_state.get("step_state", "1")

    # 진행 상황 표시
    step_names = {
        "1": "직업 선택", "2": "가치관 선택", "3": "이슈 파악",
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

        if st.button("🔄 처음부터 다시 시작"):
            st.session_state.clear()
            st.rerun()

    # 단계별 함수 실행
    step_functions = {
        "1": web_select_career,
        "2": web_select_career_values,
        "3": web_select_career_issues,
        "4": web_select_career_exploration,
        "5": web_select_career_final_goal,
        "6": web_select_career_middle_goal,
        "7": web_select_career_final_report
    }

    if current_step in step_functions:
        step_functions[current_step](st.session_state.career_state)
    elif current_step == "completed":
        st.success("🎉 모든 단계가 완료되었습니다!")
        st.write("진로 탐구를 성공적으로 마쳤습니다. 수고하셨습니다!")

if __name__ == "__main__":
    main()
