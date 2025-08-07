
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
    career_projects: Annotated[list[str], "실행 가능한 프로젝트 주제들, 다중 선택 가능"]  # 새로 추가
    career_projects_generated: Annotated[list[list[str]], "LLM으로 생성된 프로젝트 목록들"]  # 새로 추가
    career_projects_count: Annotated[int, "프로젝트 생성 횟수 (최대 5회)"]  # 새로 추가
    career_final_goal: Annotated[str, "직업 탐구 최종 목표"]
    career_final_goals_generated: Annotated[list[str], "LLM으로 생성된 최종 목표들"]  # 새로 추가
    career_final_goals_count: Annotated[int, "최종 목표 생성 횟수 (최대 5회)"]  # 새로 추가
    career_middle_goal: Annotated[list[str], "직업 탐구 중간 목표"]
    career_middle_goals_generated: Annotated[list[list[str]], "LLM으로 생성된 중간 목표 목록들"]  # 새로 추가
    career_middle_goals_count: Annotated[int, "중간 목표 생성 횟수 (최대 5회)"]  # 새로 추가
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

def shorten_goal_text(text: str) -> str:
    """목표 텍스트를 60자 이내로 단축"""
    # 핵심 키워드 매핑 (더 구체적이고 자세한 표현)
    keywords_map = {
        "전문가": "전문가로 성장하여 사회에 기여하기",
        "개발자": "개발자로서 혁신적인 솔루션 개발하기", 
        "리더": "리더십을 발휘하여 팀을 이끄는 역할 수행하기",
        "봉사": "봉사활동을 통해 지역사회 발전에 기여하기",
        "해결": "문제 해결 전문가로서 실질적 개선안 제시하기",
        "교육": "교육 분야에서 혁신적인 교수법 개발하기",
        "창업": "창업을 통해 새로운 가치 창출하기",
        "연구": "연구 활동으로 학문적 성과 달성하기",
        "멘토": "멘토로서 후배들의 성장을 도와주기",
        "기획": "기획 전문가로서 프로젝트 성공 이끌기",
        "관리": "관리 전문가로서 효율적 시스템 구축하기"
    }
    
    # 키워드 기반 단축
    for keyword, short_form in keywords_map.items():
        if keyword in text:
            if "3년" in text:
                return f"3년 내 {short_form}"
            else:
                return short_form
    
    # 일반적인 단축 규칙
    if "되기" in text:
        # "OO이 되기" 형태를 더 구체적으로 확장
        parts = text.split()
        if len(parts) > 1:
            expanded = f"3년 내 {parts[-2]} {parts[-1]}를 통해 전문성을 갖춘 인재로 성장하기"
            return expanded if len(expanded) <= 60 else text[:60]
    
    # 최후 수단: 60자로 자르기
    return text[:60]

def shorten_project_text(text: str) -> str:
    """프로젝트 텍스트를 20자 이내로 단축"""
    # 핵심 키워드 매핑
    keywords_map = {
        "체험": "체험 프로그램",
        "인터뷰": "인터뷰 프로젝트",
        "영상": "영상 제작",
        "캠페인": "홍보 캠페인",
        "제안서": "개선 제안서",
        "앱": "앱 기획",
        "웹사이트": "웹사이트 제작",
        "조사": "실태 조사",
        "연구": "연구 보고서",
        "분석": "데이터 분석",
        "설문": "설문 조사",
        "기획": "기획서 작성",
        "프로그램": "프로그램 개발",
        "교육": "교육 자료 제작",
        "봉사": "자원봉사 활동"
    }
    
    # 키워드 기반 단축
    for keyword, short_form in keywords_map.items():
        if keyword in text:
            return short_form
    
    # 일반적인 단축 규칙
    if "개발" in text:
        return "개발 프로젝트"
    elif "제작" in text:
        return "제작 프로젝트"
    elif "작성" in text:
        return "작성 프로젝트"
    elif "활동" in text:
        return "실습 활동"
    
    # 최후 수단: 20자로 자르기
    return text[:20]

def shorten_issue_text(text: str) -> str:
    """개선된 이슈 텍스트를 30자 이내로 단축"""
    # 핵심 키워드 매핑
    keywords_map = {
        "디지털": "디지털 격차 해소 필요",
        "정신": "정신 건강 관리 체계 구축", 
        "스트레스": "스트레스 관리 방안 필요",
        "협력": "지역 협력 체계 부족 문제",
        "다양성": "교육 다양성 확대 필요",
        "전문성": "전문성 향상 기회 확대",
        "연수": "연수 기회 확대 필요",
        "불평등": "학습 기회 불평등 해소",
        "커리큘럼": "커리큘럼 현대화 필요",
        "인력": "인력 부족 문제 해결",
        "처우": "처우 개선 및 복지 확대",
        "기술": "신기술 적응 교육 필요",
        "교육": "교육 체계 개선 방안",
        "환경": "근무 환경 개선 필요",
        "소통": "소통 체계 개선 필요",
        "감염": "감염 관리 강화 방안"
    }
    
    # 키워드 기반 단축
    for keyword, short_form in keywords_map.items():
        if keyword in text:
            return short_form
    
    # 일반적인 단축 규칙
    if "부족" in text:
        if "기회" in text:
            return "기회 부족 문제 해결 방안"
        else:
            return "부족 문제 해결 방안 모색"
    
    if "개선" in text:
        return "개선 방안 연구 필요"
    
    if "문제" in text:
        return "문제 해결 방안 연구"
    
    # 최후 수단: 30자로 자르기
    return text[:30]

def generate_career_issues_with_llm(career: str, career_values: list, previous_issues: list | None = None) -> list:
    """LLM을 사용하여 직업 이슈 생성"""
    if previous_issues is None:
        previous_issues = []

    # 이전에 생성된 모든 이슈들을 평탄화
    all_previous_issues = []
    for issues_list in previous_issues:
        all_previous_issues.extend(issues_list)

    prompt = f"""
당신은 진로 상담 전문가입니다. 한국 고등학생이 이해하기 쉬운 {career} 분야의 현재 이슈 5가지를 제시해주세요.

**직업**: {career}
**가치관**: {', '.join(career_values)}

**중요한 요구사항**:
1. 한국 고등학생 수준의 쉬운 용어만 사용
2. 각 이슈는 **반드시 30자 이내**로 작성
3. 현재 한국에서 실제 논의되는 문제
4. 간단명료하게 핵심만 표현

**중복 방지**: 다음과 다른 새로운 이슈를 제시하세요:
{', '.join(all_previous_issues) if all_previous_issues else '없음'}

**응답 형식 (반드시 30자 이내)**: 
- 이슈1
- 이슈2  
- 이슈3
- 이슈4
- 이슈5

**좋은 예시** (요양보호사):
- 인력 부족 문제 해결 방안
- 처우 개선 및 복지 확대
- 디지털 기술 도입 필요성
- 감염 관리 강화 방안
- 정신 건강 지원 체계 구축

**나쁜 예시** (너무 길음):
- 고령화 사회에 따른 요양보호사 인력 부족 문제
- 요양보호사의 근무 환경 및 처우 개선 필요성
"""

    try:
        response = llm.invoke(prompt)
        generated_text = response.content
        
        # content가 문자열인지 확인
        if isinstance(generated_text, list):
            generated_text = ' '.join(str(item) for item in generated_text)
        elif not isinstance(generated_text, str):
            generated_text = str(generated_text)

        # 응답에서 이슈 추출 및 15자 이내로 강제 조정
        issues = []
        for line in generated_text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                # '-' 또는 '•' 제거하고 이슈 추출
                issue = line[1:].strip()
                if issue and len(issue) > 5:  # 최소 길이 확인
                    # 30자 이내로 강제 단축
                    if len(issue) > 30:
                        issue = shorten_issue_text(issue)
                    issues.append(issue)

        # 5개가 아닌 경우 조정
        if len(issues) < 5:
            career_short = career[:4] if len(career) > 4 else career  # 직업명 단축
            default_issues = [
                f"{career_short} 인력 부족 해결 방안",
                f"{career_short} 처우 개선 필요성", 
                f"{career_short} 기술 변화 대응",
                f"{career_short} 교육 기회 확대",
                f"{career_short} 미래 전망 불안"
            ]
            issues.extend(default_issues[len(issues):])
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
            state = new_state  # type: ignore

    # 현재 이슈 표시 및 다중 선택
    current_issues = state.get('career_issues', [])
    selected_issues = []
    
    if current_issues:
        st.subheader("🔍 AI가 분석한 주요 이슈들")
        
        # 다중 선택 체크박스
        selected_issues = st.multiselect(
            "관심 있는 이슈를 모두 선택하세요 (여러 개 선택 가능):",
            current_issues,
            key="selected_issues",
            help="탐구하고 싶은 이슈들을 선택해주세요. 여러 개를 선택할 수 있습니다."
        )
        
        # 선택된 이슈 미리보기
        if selected_issues:
            st.success(f"✅ 선택된 이슈 ({len(selected_issues)}개):")
            for i, issue in enumerate(selected_issues, 1):
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
            if current_issues and selected_issues:  # 선택된 이슈가 있는지 확인
                new_state = {
                    **state,
                    "step_state": "4",
                    "career_issues": selected_issues,  # 선택된 이슈들로 업데이트
                    "is_react": False,
                    "messages": state.get("messages", []) + [f"관심 이슈를 선택했습니다: {', '.join(selected_issues)} ({career_issues_count}/5회 생성)"]
                }
                st.session_state.career_state = new_state
                st.success(f"✅ {len(selected_issues)}개의 이슈를 선택했습니다!")
                st.rerun()
                return new_state
            elif current_issues and not selected_issues:
                st.error("최소 하나의 이슈를 선택해주세요!")
            else:
                st.error("이슈가 생성되지 않았습니다. 다시 시도해주세요.")

    return state

def generate_career_projects_with_llm(career: str, career_values: list, career_issues: list, previous_projects: list | None = None) -> list:
    """LLM을 사용하여 실행 가능한 프로젝트 생성"""
    if previous_projects is None:
        previous_projects = []

    # 이전에 생성된 모든 프로젝트들을 평탄화
    all_previous_projects = []
    for projects_list in previous_projects:
        all_previous_projects.extend(projects_list)

    prompt = f"""
당신은 진로 상담 전문가입니다. 한국 고등학생이 실제로 실행할 수 있는 {career} 직업 관련 프로젝트 5가지를 제시해주세요.

**직업**: {career}
**가치관**: {', '.join(career_values)}
**해결하고자 하는 이슈**: {', '.join(career_issues)}

**중요한 요구사항**:
1. 고등학생이 실제로 실행 가능한 구체적인 프로젝트
2. 선택된 이슈들을 해결하는데 도움이 되는 프로젝트
3. 각 프로젝트는 **반드시 20자 이내**로 간단명료하게 표현
4. 실제 현장에서 의미 있는 결과를 만들 수 있는 프로젝트
5. 고등학생 수준에서 실현 가능한 범위

**중복 방지**: 다음과 다른 새로운 프로젝트를 제시하세요:
{', '.join(all_previous_projects) if all_previous_projects else '없음'}

**응답 형식 (반드시 20자 이내)**:
- 프로젝트1
- 프로젝트2
- 프로젝트3
- 프로젝트4
- 프로젝트5

**좋은 예시** (요양보호사, 인력 부족 문제):
- 요양원 자원봉사 체험
- 고령자 돌봄 앱 기획
- 요양보호사 인터뷰 영상
- 요양보호사 홍보 캠페인
- 노인 돌봄 개선 제안서

**나쁜 예시** (너무 복잡하거나 비현실적):
- 국가 차원의 요양보호사 정책 개발 및 시행 계획서
- 대규모 요양원 설립 및 운영 사업계획서 작성
"""

    try:
        response = llm.invoke(prompt)
        generated_text = response.content
        
        # content가 문자열인지 확인
        if isinstance(generated_text, list):
            generated_text = ' '.join(str(item) for item in generated_text)
        elif not isinstance(generated_text, str):
            generated_text = str(generated_text)

        # 응답에서 프로젝트 추출
        projects = []
        for line in generated_text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                # '-' 또는 '•' 제거하고 프로젝트 추출
                project = line[1:].strip()
                if project and len(project) > 3:  # 최소 길이 확인
                    # 20자 이내로 강제 단축
                    if len(project) > 20:
                        project = shorten_project_text(project)
                    projects.append(project)

        # 5개가 아닌 경우 조정
        if len(projects) < 5:
            career_short = career[:4] if len(career) > 4 else career
            default_projects = [
                f"{career_short} 체험 프로그램",
                f"{career_short} 인터뷰 영상",
                f"{career_short} 홍보 캠페인",
                f"{career_short} 개선 제안서",
                f"{career_short} 연구 보고서"
            ]
            projects.extend(default_projects[len(projects):])
        elif len(projects) > 5:
            projects = projects[:5]

        return projects

    except Exception as e:
        st.error(f"프로젝트 생성 중 오류가 발생했습니다: {e}")
        # 실패 시 기본 프로젝트 반환
        career_short = career[:4] if len(career) > 4 else career
        return [
            f"{career_short} 체험 프로그램",
            f"{career_short} 인터뷰 프로젝트",
            f"{career_short} 홍보 활동",
            f"{career_short} 개선 제안",
            f"{career_short} 연구 활동"
        ]

def web_select_career_exploration(state: CareerState) -> CareerState:
    """웹에서 실행 가능한 프로젝트 선택 함수 - LLM 기반 동적 생성"""
    st.header("4단계: 실행 가능한 프로젝트 선택 (AI 기반)")
    st.write(f"**선택한 직업:** {state.get('career', '')}")
    st.write(f"**선택한 가치관:** {', '.join(state.get('career_values', []))}")
    st.write(f"**선택한 이슈:** {', '.join(state.get('career_issues', []))}")

    career_projects_count = state.get('career_projects_count', 0)
    career_projects_generated = state.get('career_projects_generated', [])

    # 프로젝트 생성 상태 표시
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"🤖 AI가 {state.get('career', '')} 직업의 실행 가능한 프로젝트를 분석 중...")
    with col2:
        st.metric("생성 횟수", f"{career_projects_count}/5")

    # 첫 실행이거나 재실행인 경우 프로젝트 생성
    if career_projects_count == 0 or state.get('generate_new_projects', False):
        if career_projects_count < 5:
            with st.spinner("AI가 실행 가능한 프로젝트를 생성하고 있습니다..."):
                new_projects = generate_career_projects_with_llm(
                    state.get('career', ''),
                    state.get('career_values', []),
                    state.get('career_issues', []),
                    career_projects_generated
                )

            # 새 프로젝트를 상태에 저장
            new_career_projects_generated = career_projects_generated + [new_projects]
            new_career_projects_count = career_projects_count + 1

            new_state = {
                **state,
                "career_projects": new_projects,
                "career_projects_generated": new_career_projects_generated,
                "career_projects_count": new_career_projects_count,
                "generate_new_projects": False
            }
            st.session_state.career_state = new_state
            state = new_state  # type: ignore

    # 현재 프로젝트 표시 및 다중 선택
    current_projects = state.get('career_projects', [])
    selected_projects = []
    
    if current_projects:
        st.subheader("🚀 AI가 분석한 실행 가능한 프로젝트들")
        
        # 다중 선택 체크박스
        selected_projects = st.multiselect(
            "관심 있는 프로젝트를 모두 선택하세요 (여러 개 선택 가능):",
            current_projects,
            key="selected_projects",
            help="실제로 실행해보고 싶은 프로젝트들을 선택해주세요. 여러 개를 선택할 수 있습니다."
        )
        
        # 선택된 프로젝트 미리보기
        if selected_projects:
            st.success(f"✅ 선택된 프로젝트 ({len(selected_projects)}개):")
            for i, project in enumerate(selected_projects, 1):
                st.write(f"**{i}.** {project}")

    # 버튼들
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 다른 프로젝트 보기", key="regenerate_projects"):
            if career_projects_count < 5:
                new_state = {
                    **state,
                    "generate_new_projects": True
                }
                st.session_state.career_state = new_state
                st.rerun()
            else:
                st.warning("최대 생성 횟수(5회)에 도달했습니다.")

    with col2:
        if st.button("📋 이전 프로젝트 보기", key="show_project_history"):
            if career_projects_generated:
                st.subheader("📚 이전에 생성된 프로젝트들")
                for i, projects in enumerate(career_projects_generated, 1):
                    with st.expander(f"{i}번째 생성 ({len(projects)}개)"):
                        for j, project in enumerate(projects, 1):
                            st.write(f"{j}. {project}")

    with col3:
        if st.button("다음 단계로", key="projects_submit"):
            if current_projects and selected_projects:  # 선택된 프로젝트가 있는지 확인
                new_state = {
                    **state,
                    "step_state": "5",
                    "career_projects": selected_projects,  # 선택된 프로젝트들로 업데이트
                    "career_exploration": f"{state.get('career', '')} 분야 실행 프로젝트 선택 완료",
                    "is_react": False,
                    "messages": state.get("messages", []) + [f"실행 프로젝트를 선택했습니다: {', '.join(selected_projects)} ({career_projects_count}/5회 생성)"]
                }
                st.session_state.career_state = new_state
                st.success(f"✅ {len(selected_projects)}개의 프로젝트를 선택했습니다!")
                st.rerun()
                return new_state
            elif current_projects and not selected_projects:
                st.error("최소 하나의 프로젝트를 선택해주세요!")
            else:
                st.error("프로젝트가 생성되지 않았습니다. 다시 시도해주세요.")

    return state

def generate_career_final_goal_with_llm(career: str, career_values: list, career_issues: list, career_projects: list, previous_goals: list | None = None) -> str:
    """LLM을 사용하여 달성 가능한 최종 목표 생성"""
    if previous_goals is None:
        previous_goals = []

    prompt = f"""
당신은 진로 상담 전문가입니다. 한국 고등학생이 실제로 달성할 수 있는 {career} 직업의 진로 목표를 한 문장으로 제시해주세요.

**직업**: {career}
**가치관**: {', '.join(career_values)}
**해결하고자 하는 이슈**: {', '.join(career_issues)}
**실행 예정인 프로젝트**: {', '.join(career_projects)}

**중요한 요구사항**:
1. 한국 고등학생이 3년 이내에 실제로 달성 가능한 현실적인 목표
2. 선택된 가치관과 이슈, 프로젝트를 반영한 구체적인 목표
3. **한 문장으로 간결하게 표현** (60자 이내)
4. 측정 가능하고 명확한 목표
5. 고등학생의 현재 수준에서 시작하여 도달 가능한 범위

**중복 방지**: 다음과 다른 새로운 목표를 제시하세요:
{', '.join(previous_goals) if previous_goals else '없음'}

**응답 형식**:
한 문장의 목표만 작성해주세요.

**좋은 예시** (소프트웨어 개발자):
- 3년 내 사회문제 해결 앱 개발자로 성장하여 지역사회에 기여하기
- 디지털 격차 해소를 위한 교육 프로그램 개발 전문가로 활동하기
- 지역사회 IT 교육 봉사단 리더로서 디지털 소외계층 지원하기
"""

    try:
        response = llm.invoke(prompt)
        generated_goal = response.content
        
        # content가 문자열인지 확인
        if isinstance(generated_goal, list):
            generated_goal = ' '.join(str(item) for item in generated_goal)
        elif not isinstance(generated_goal, str):
            generated_goal = str(generated_goal)
        
        generated_goal = generated_goal.strip()

        # 응답 정제 (불필요한 문구 제거)
        if generated_goal.startswith('-'):
            generated_goal = generated_goal[1:].strip()
        if generated_goal.startswith('•'):
            generated_goal = generated_goal[1:].strip()

        # 30자 이내로 단축
        if len(generated_goal) > 60:
            generated_goal = shorten_goal_text(generated_goal)

        return generated_goal

    except Exception as e:
        st.error(f"목표 생성 중 오류가 발생했습니다: {e}")
        # 실패 시 기본 목표 반환
        career_short = career[:4] if len(career) > 4 else career
        return f"3년 내 {career_short} 전문가 되기"

def web_select_career_final_goal(state: CareerState) -> CareerState:
    """웹에서 최종 목표 설정 함수 - LLM 기반 동적 생성"""
    st.header("5단계: 최종 목표 설정 (AI 기반)")
    st.write(f"**선택한 직업:** {state.get('career', '')}")
    st.write(f"**선택한 가치관:** {', '.join(state.get('career_values', []))}")
    st.write(f"**선택한 이슈:** {', '.join(state.get('career_issues', []))}")
    st.write(f"**선택한 프로젝트:** {', '.join(state.get('career_projects', []))}")

    career_final_goals_count = state.get('career_final_goals_count', 0)
    career_final_goals_generated = state.get('career_final_goals_generated', [])

    # 목표 생성 상태 표시
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"🤖 AI가 {state.get('career', '')} 직업의 달성 가능한 진로 목표를 분석 중...")
    with col2:
        st.metric("생성 횟수", f"{career_final_goals_count}/5")

    # 첫 실행이거나 재실행인 경우 목표 생성
    if career_final_goals_count == 0 or state.get('generate_new_goal', False):
        if career_final_goals_count < 5:
            with st.spinner("AI가 달성 가능한 진로 목표를 생성하고 있습니다..."):
                new_goal = generate_career_final_goal_with_llm(
                    state.get('career', ''),
                    state.get('career_values', []),
                    state.get('career_issues', []),
                    state.get('career_projects', []),
                    career_final_goals_generated
                )

            # 새 목표를 상태에 저장
            new_career_final_goals_generated = career_final_goals_generated + [new_goal]
            new_career_final_goals_count = career_final_goals_count + 1

            new_state = {
                **state,
                "career_final_goal": new_goal,
                "career_final_goals_generated": new_career_final_goals_generated,
                "career_final_goals_count": new_career_final_goals_count,
                "generate_new_goal": False
            }
            st.session_state.career_state = new_state
            state = new_state  # type: ignore

    # 현재 목표 표시
    current_goal = state.get('career_final_goal', '')
    if current_goal:
        st.subheader("🎯 AI가 제안한 달성 가능한 진로 목표")
        
        # 목표를 강조 표시
        st.success(f"**📌 {current_goal}**")
        
        # 목표 분석 정보 제공
        goal_length = len(current_goal)
        st.info(f"💡 **목표 분석**: {goal_length}자 / 한국 고등학생 달성 가능 수준")

    # 버튼들
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 다른 목표 보기", key="regenerate_goal"):
            if career_final_goals_count < 5:
                new_state = {
                    **state,
                    "generate_new_goal": True
                }
                st.session_state.career_state = new_state
                st.rerun()
            else:
                st.warning("최대 생성 횟수(5회)에 도달했습니다.")

    with col2:
        if st.button("📋 이전 목표 보기", key="show_goal_history"):
            if career_final_goals_generated:
                st.subheader("📚 이전에 생성된 목표들")
                for i, goal in enumerate(career_final_goals_generated, 1):
                    st.write(f"{i}. {goal}")

    with col3:
        if st.button("다음 단계로", key="goal_submit"):
            if current_goal:
                new_state = {
                    **state,
                    "step_state": "6",
                    "is_react": False,
                    "messages": state.get("messages", []) + [f"진로 목표를 설정했습니다: {current_goal} ({career_final_goals_count}/5회 생성)"]
                }
                st.session_state.career_state = new_state
                st.success(f"✅ 진로 목표: {current_goal}")
                st.rerun()
                return new_state
            else:
                st.error("목표가 생성되지 않았습니다. 다시 시도해주세요.")

    return state

def shorten_middle_goal_text(text: str, max_length: int = 40) -> str:
    """중간 목표 텍스트를 지정된 길이로 단축하는 함수"""
    if len(text) <= max_length:
        return text
    
    # 문장부호나 공백에서 잘라내기
    for i in range(max_length - 3, max_length // 2, -1):
        if text[i] in ['다', '요', '기', '함', '성', '력', '습', '득']:
            return text[:i+1]
    
    # 찾을 수 없으면 강제로 자르고 생략표시 추가
    return text[:max_length-2] + "기"

def generate_career_middle_goals_with_llm(career: str, career_values: list, career_issues: list, career_projects: list, career_final_goal: str, previous_goals: list | None = None) -> list:
    """LLM을 사용하여 중간 목표 3개 생성 (3가지 역량 기반)"""
    if previous_goals is None:
        previous_goals = []

    # 이전에 생성된 모든 중간 목표들을 평탄화
    all_previous_goals = []
    for goals_list in previous_goals:
        all_previous_goals.extend(goals_list)

    prompt = f"""
당신은 진로 상담 전문가입니다. 한국 고등학생이 실제로 달성할 수 있는 {career} 직업의 중간 목표 3개를 제시해주세요.

**직업**: {career}
**가치관**: {', '.join(career_values)}
**해결하고자 하는 이슈**: {', '.join(career_issues)}
**실행 예정인 프로젝트**: {', '.join(career_projects)}
**최종 목표**: {career_final_goal}

**중요한 요구사항**:
최종 목표를 실현하기 위해 고등학생 수준에서 길러야 할 **핵심 역량 기반 중간 목표 3개**를 다음 형식으로 제시해주세요:

[1] **학업역량**을 포함하는 내용으로 제시 (관련 지식 습득, 학습 능력 향상 등)
[2] **진로역량**을 포함하는 내용으로 제시 (진로 탐색, 전문성 개발, 실무 경험 등)  
[3] **공동체역량**을 포함하는 내용으로 제시 (협업, 소통, 사회적 책임 등)

각 목표는 **반드시 40자 이내**로 간단명료하게 표현해주세요.
실제로 고등학생이 3년 이내에 달성 가능한 현실적인 목표여야 합니다.

**중복 방지**: 다음과 다른 새로운 목표들을 제시하세요:
{', '.join(all_previous_goals) if all_previous_goals else '없음'}

**응답 형식**:
[1] (학업역량 관련 목표)
[2] (진로역량 관련 목표)
[3] (공동체역량 관련 목표)

**좋은 예시** (소프트웨어 개발자):
[1] 프로그래밍 언어 3개 이상 능숙하게 다루기
[2] 실제 앱 개발 프로젝트 3개 이상 완성하기
[3] 지역 IT 봉사활동 리더로 활동하기
"""

    try:
        response = llm.invoke(prompt)
        generated_text = response.content
        
        # content가 문자열인지 확인
        if isinstance(generated_text, list):
            generated_text = ' '.join(str(item) for item in generated_text)
        elif not isinstance(generated_text, str):
            generated_text = str(generated_text)
        
        # 응답에서 목표 3개 추출
        goals = []
        for line in generated_text.split('\n'):
            line = line.strip()
            if line.startswith('[1]') or line.startswith('[2]') or line.startswith('[3]'):
                # [1], [2], [3] 제거하고 목표 추출
                goal = line[3:].strip()
                if goal and len(goal) > 3:  # 최소 길이 확인
                    # 40자 이내로 강제 단축
                    if len(goal) > 40:
                        goal = shorten_middle_goal_text(goal)
                    goals.append(goal)

        # 3개가 아닌 경우 조정
        if len(goals) < 3:
            # 기본 목표로 보완
            career_short = career[:4] if len(career) > 4 else career
            default_goals = [
                f"{career_short} 관련 전문 지식 습득하기",
                f"{career_short} 실무 경험 3회 이상 쌓기", 
                f"{career_short} 관련 봉사활동 참여하기"
            ]
            goals.extend(default_goals[len(goals):])
        elif len(goals) > 3:
            goals = goals[:3]

        return goals

    except Exception as e:
        st.error(f"중간 목표 생성 중 오류가 발생했습니다: {e}")
        # 실패 시 기본 목표 반환
        career_short = career[:4] if len(career) > 4 else career
        return [
            f"{career_short} 관련 전문 지식 습득하기",
            f"{career_short} 실무 경험 3회 이상 쌓기",
            f"{career_short} 관련 봉사활동 참여하기"
        ]

def web_select_career_middle_goal(state: CareerState) -> CareerState:
    """웹에서 중간 목표 설정 함수 - LLM 기반 동적 생성"""
    st.header("6단계: 중간 목표 설정 (AI 기반)")
    st.write(f"**선택한 직업:** {state.get('career', '')}")
    st.write(f"**선택한 가치관:** {', '.join(state.get('career_values', []))}")
    st.write(f"**선택한 이슈:** {', '.join(state.get('career_issues', []))}")
    st.write(f"**선택한 프로젝트:** {', '.join(state.get('career_projects', []))}")
    st.write(f"**최종 목표:** {state.get('career_final_goal', '')}")

    career_middle_goals_count = state.get('career_middle_goals_count', 0)
    career_middle_goals_generated = state.get('career_middle_goals_generated', [])

    # 목표 생성 상태 표시
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"🤖 AI가 {state.get('career', '')} 직업의 3가지 핵심 역량 기반 중간 목표를 분석 중...")
    with col2:
        st.metric("생성 횟수", f"{career_middle_goals_count}/5")

    # 첫 실행이거나 재실행인 경우 목표 생성
    if career_middle_goals_count == 0 or state.get('generate_new_middle_goals', False):
        if career_middle_goals_count < 5:
            with st.spinner("AI가 3가지 핵심 역량 기반 중간 목표를 생성하고 있습니다..."):
                new_goals = generate_career_middle_goals_with_llm(
                    state.get('career', ''),
                    state.get('career_values', []),
                    state.get('career_issues', []),
                    state.get('career_projects', []),
                    state.get('career_final_goal', ''),
                    career_middle_goals_generated
                )

            # 새 목표들을 상태에 저장
            new_career_middle_goals_generated = career_middle_goals_generated + [new_goals]
            new_career_middle_goals_count = career_middle_goals_count + 1

            new_state = {
                **state,
                "career_middle_goal": new_goals,
                "career_middle_goals_generated": new_career_middle_goals_generated,
                "career_middle_goals_count": new_career_middle_goals_count,
                "generate_new_middle_goals": False
            }
            st.session_state.career_state = new_state
            state = new_state  # type: ignore

    # 현재 목표들 표시
    current_goals = state.get('career_middle_goal', [])
    if current_goals:
        st.subheader("🎯 AI가 제안한 3가지 핵심 역량 기반 중간 목표")
        
        # 목표들을 역량별로 구분하여 표시
        competency_labels = ["📚 학업역량", "💼 진로역량", "🤝 공동체역량"]
        for i, (goal, label) in enumerate(zip(current_goals, competency_labels)):
            st.success(f"**{label}**: {goal}")
        
        # 목표 분석 정보 제공
        total_length = sum(len(goal) for goal in current_goals)
        st.info(f"💡 **목표 분석**: 총 {len(current_goals)}개 / 평균 {total_length//len(current_goals)}자 / 고등학생 달성 가능 수준")

    # 버튼들
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 다른 목표 보기", key="regenerate_middle_goals"):
            if career_middle_goals_count < 5:
                new_state = {
                    **state,
                    "generate_new_middle_goals": True
                }
                st.session_state.career_state = new_state
                st.rerun()
            else:
                st.warning("최대 생성 횟수(5회)에 도달했습니다.")

    with col2:
        if st.button("📋 이전 목표 보기", key="show_middle_goals_history"):
            if career_middle_goals_generated:
                st.subheader("📚 이전에 생성된 중간 목표들")
                for i, goals in enumerate(career_middle_goals_generated, 1):
                    with st.expander(f"{i}번째 생성 ({len(goals)}개)"):
                        for j, goal in enumerate(goals, 1):
                            st.write(f"{j}. {goal}")

    with col3:
        if st.button("다음 단계로", key="middle_goals_submit"):
            if current_goals:
                new_state = {
                    **state,
                    "step_state": "7",
                    "is_react": False,
                    "messages": state.get("messages", []) + [f"중간 목표를 설정했습니다: {', '.join(current_goals)} ({career_middle_goals_count}/5회 생성)"]
                }
                st.session_state.career_state = new_state
                st.success(f"✅ 중간 목표 ({len(current_goals)}개): {', '.join(current_goals)}")
                st.rerun()
                return new_state
            else:
                st.error("목표가 생성되지 않았습니다. 다시 시도해주세요.")

    return state

def web_select_career_final_report(state: CareerState) -> CareerState:
    """웹에서 직업 탐구 최종 보고서 작성 함수"""
    st.header("7단계: 직업 탐구 최종 보고서")

    st.subheader("📋 탐구 정보 요약")
    st.write(f"**직업:** {state.get('career', '')}")
    st.write(f"**가치관:** {', '.join(state.get('career_values', []))}")
    st.write(f"**이슈:** {', '.join(state.get('career_issues', []))}")
    st.write(f"**프로젝트:** {', '.join(state.get('career_projects', []))}")
    st.write(f"**최종 목표:** {state.get('career_final_goal', '')}")
    st.write(f"**중간 목표:** {', '.join(state.get('career_middle_goal', []))}")

    st.subheader("📝 최종 보고서 작성")
    report_input = st.text_area(
        "위 정보를 바탕으로 직업 탐구 보고서를 작성해주세요:",
        placeholder="AI와 함께한 탐구 과정에서 배운 점, 느낀 점, 앞으로의 계획 등을 포함하여 보고서를 작성해주세요.",
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
                "messages": state.get("messages", []) + ["AI와 함께한 최종 보고서를 작성했습니다."]
            }
            st.session_state.career_state = new_state
            st.success("✅ AI 진로 탐구가 완료되었습니다!")
            st.balloons()
            st.subheader("🎉 AI 진로 탐구 완료!")
            return new_state  # type: ignore
        else:
            st.error("보고서를 작성해주세요!")
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
            "career_projects": [],  # 추가
            "career_projects_generated": [],  # 추가
            "career_projects_count": 0,  # 추가
            "career_final_goal": "",
            "career_final_goals_generated": [],  # 추가
            "career_final_goals_count": 0,  # 추가
            "career_middle_goal": [],
            "career_middle_goals_generated": [],  # 새로 추가
            "career_middle_goals_count": 0,  # 새로 추가
            "career_final_report": "",
            "messages": ["AI 진로 탐구를 시작합니다."],
            "generate_new": False,
            "generate_new_projects": False,  # 추가
            "generate_new_goal": False,  # 추가
            "generate_new_middle_goals": False  # 새로 추가
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

        # AI 생성 상태 표시
        if current_step == "3":
            issues_count = st.session_state.career_state.get('career_issues_count', 0)
            st.info(f"🤖 AI 이슈 생성: {issues_count}/5회")
        elif current_step == "4":
            projects_count = st.session_state.career_state.get('career_projects_count', 0)
            st.info(f"🤖 AI 프로젝트 생성: {projects_count}/5회")
        elif current_step == "5":
            goals_count = st.session_state.career_state.get('career_final_goals_count', 0)
            st.info(f"🤖 AI 목표 생성: {goals_count}/5회")
        elif current_step == "6":
            middle_goals_count = st.session_state.career_state.get('career_middle_goals_count', 0)
            st.info(f"🤖 AI 중간 목표 생성: {middle_goals_count}/5회")

        if st.button("🔄 처음부터 다시 시작"):
            st.session_state.clear()
            st.rerun()

    # 단계별 함수 실행
    step_functions = {
        "1": web_select_career,
        "2": web_select_career_values,
        "3": web_select_career_issues,
        "4": web_select_career_exploration,
        "5": web_select_career_final_goal,  # 5단계 추가!
        "6": web_select_career_middle_goal,  # 6단계 추가!
        "7": web_select_career_final_report   # 7단계 추가!
    }

    if current_step in step_functions:
        step_functions[current_step](st.session_state.career_state)  # type: ignore
    elif current_step == "completed":
        st.success("🎉 모든 단계가 완료되었습니다!")
        st.write("AI와 함께한 진로 탐구를 성공적으로 마쳤습니다. 수고하셨습니다!")

if __name__ == "__main__":
    main()
