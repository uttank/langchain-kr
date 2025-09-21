from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

# 상태 정의
class State(TypedDict):
    messages: Annotated[list, add_messages]
    career: Annotated[str, "학생이 선택한 직업"]
    career_values: Annotated[list[str], "직업에 대한 가치관"]
    career_issues: Annotated[list[str], "직업 관련 이슈들"]

# 진로 상담사 시스템 프롬프트
CAREER_COUNSELOR_PROMPT = """
당신은 대한민국 고등학생들의 진로를 상담해주는 전문 상담사입니다.

**역할과 전문성:**
- 20년 이상의 진로 상담 경험을 가진 전문가
- 대한민국 교육 시스템과 대학 입시에 대한 깊은 이해
- 다양한 직업군과 산업 동향에 대한 전문 지식

**상담 원칙:**
1. 학생의 관심사, 적성, 가치관을 종합적으로 고려
2. 현실적이고 구체적인 조언 제공
3. 학생의 자율성과 선택권을 존중
4. 긍정적이고 격려하는 태도 유지
5. 객관적이고 균형잡힌 정보 제공

**상담 영역:**
- 전공 선택 및 대학 진학 상담
- 직업 탐색 및 진로 설계
- 학습 계획 및 진로 준비 방법
- 적성 검사 결과 해석
- 진로 관련 고민 상담

**응답 스타일:**
- 친근하고 이해하기 쉬운 언어 사용
- 학생의 입장에서 공감하며 소통
- 구체적인 예시와 실용적인 조언 제공
- 질문을 통해 학생의 생각을 이끌어내기

학생이 진로에 대해 고민하고 있다면, 먼저 학생의 이야기를 충분히 들어보고 적절한 질문을 통해 상담을 진행해주세요.
"""

def get_job_specific_prompt(career: str, career_values: list, career_issues: list) -> str:
    """특정 직업과 가치관, 이슈에 대한 맞춤형 프롬프트 생성"""
    job_specific_prompt = f"""
**학생 정보:**
- 희망 직업: {career}
- 선택한 가치관: {', '.join(career_values) if career_values else '없음'}
- 관심 있는 이슈: {', '.join(career_issues) if career_issues else '없음'}

이 정보를 바탕으로 다음 사항들을 중심으로 맞춤형 상담을 제공해주세요:

**직업 분석:**
1. {career}의 특성과 주요 업무
2. 필요한 역량과 자질
3. 진입 경로와 자격 요건
4. 전망과 발전 가능성

**가치관 기반 조언:**
- 선택한 가치관이 해당 직업에서 어떻게 실현될 수 있는지
- 가치관에 맞는 구체적인 준비 방향 제시

**이슈 중심 상담:**
- 관심 있는 이슈들에 대한 현실적 분석
- 이슈 해결에 기여할 수 있는 방법 제시

**진로 준비 방안:**
1. 추천 전공 및 학과
2. 관련 자격증 및 시험
3. 경험 쌓기 방법 (인턴십, 봉사활동 등)
4. 고등학교 시절 할 수 있는 준비

**현실적 조언:**
1. 해당 직업의 장단점
2. 대안 직업군 제시
3. 단계별 목표 설정 방법
4. 학습 계획 및 시간 관리

구체적이고 실용적인 조언을 통해 학생이 꿈을 향해 나아갈 수 있도록 도와주세요.
"""
    return CAREER_COUNSELOR_PROMPT + "\n" + job_specific_prompt

def get_desired_job() -> str:
    """학생의 희망 직업 입력받기 (다시선택 기능 포함)"""
    while True:
        print("🎯 1단계: 관심있는 직업이나 꿈꾸는 직업이 있나요?")
        print("(예: 의사, 교사, 개발자, 디자이너 등)\n")
        
        desired_job = input("직업을 입력해주세요: ").strip()
        
        if desired_job:
            print(f"\n✨ '{desired_job}'에 관심이 있으시는군요!")
            
            # 확인 및 다시선택 옵션
            while True:
                choice = input("\n1. 이 직업으로 진행하기\n2. 다시 선택하기\n선택 (1/2): ").strip()
                
                if choice == "1":
                    return desired_job
                elif choice == "2":
                    print("\n🔄 직업을 다시 선택하겠습니다.\n")
                    break
                else:
                    print("1 또는 2를 입력해주세요.")
        else:
            print("직업명을 입력해주세요. 구체적이지 않아도 괜찮습니다!\n")

def get_career_values(career: str) -> list[str]:
    """학생의 직업 가치관 선택받기 (다시선택 기능 포함)"""
    value_options = {
        "1": "경제적 가치 - 높은 수입, 안정적인 직업",
        "2": "사회적 가치 - 사회에 긍정적인 영향, 봉사", 
        "3": "공동체적 가치 - 사람들과 협력, 소통",
        "4": "능력 발휘 - 나의 재능과 역량을 최대한 발휘",
        "5": "자율·창의성 - 독립적으로 일하고 새로운 아이디어 창출",
        "6": "미래 비전 - 성장 가능성, 혁신적인 분야"
    }
    
    while True:
        print(f"\n📊 2단계: '{career}' 직업을 선택할 때 고려했던 가치관을 선택해주세요.")
        print("여러 개 선택할 수 있습니다. (숫자로 입력, 예: 1,3,5)\n")
        
        for key, value in value_options.items():
            print(f"{key}. {value}")
        
        selections = input("\n선택한 번호를 입력하세요 (예: 1,3,5): ").strip()
        
        if not selections:
            print("최소 하나는 선택해주세요!")
            continue
            
        try:
            selected_numbers = [num.strip() for num in selections.split(',')]
            selected_values = []
            
            for num in selected_numbers:
                if num in value_options:
                    selected_values.append(f"{num}. {value_options[num]}")
                else:
                    print(f"'{num}'은 유효하지 않은 번호입니다. 1-6 사이의 번호를 입력해주세요.")
                    break
            else:
                if selected_values:
                    print(f"\n💝 선택한 가치관:")
                    for value in selected_values:
                        print(f"  - {value}")
                    
                    # 확인 및 다시선택 옵션
                    while True:
                        choice = input("\n1. 이 가치관들로 진행하기\n2. 다시 선택하기\n선택 (1/2): ").strip()
                        
                        if choice == "1":
                            return selected_values
                        elif choice == "2":
                            print("\n🔄 가치관을 다시 선택하겠습니다.\n")
                            break
                        else:
                            print("1 또는 2를 입력해주세요.")
                    break
                    
        except Exception as e:
            print("올바른 형식으로 입력해주세요. (예: 1,3,5)")

def generate_career_issues(career: str, career_values: list, previous_issues: list = None) -> list[str]:
    """AI를 사용하여 직업 관련 이슈 생성 (중복 방지)"""
    if previous_issues is None:
        previous_issues = []
    
    # 가치관에 따른 맞춤형 컨텍스트
    value_context = ""
    for value in career_values:
        if "경제적 가치" in value:
            value_context += "경제적 안정성과 수입 관련 이슈, "
        elif "사회적 가치" in value:
            value_context += "사회적 기여와 봉사 관련 이슈, "
        elif "공동체적 가치" in value:
            value_context += "협력과 소통 관련 이슈, "
        elif "능력 발휘" in value:
            value_context += "전문성 개발과 역량 강화 관련 이슈, "
        elif "자율·창의성" in value:
            value_context += "창의성과 자율성 관련 이슈, "
        elif "미래 비전" in value:
            value_context += "미래 성장성과 혁신 관련 이슈, "
    
    # 중복 방지를 위한 이전 이슈 목록 정리
    previous_issues_text = ""
    if previous_issues:
        previous_issues_text = f"""
**중복 방지**: 다음과 의미나 단어가 중복되지 않는 완전히 새로운 이슈를 제시해주세요:
{', '.join(previous_issues)}

위 이슈들과 유사한 주제나 단어는 절대 사용하지 마세요.
"""
    
    prompt = f"""
당신은 진로 상담 전문가입니다. 한국 고등학생이 탐구할 만한 {career} 분야의 현재 이슈 5가지를 제시해주세요.

**직업**: {career}
**선택한 가치관**: {', '.join(career_values)}

{previous_issues_text}

**요구사항**:
1. 한국 고등학생 수준에서 이해하기 쉬운 이슈
2. 현재 한국에서 실제로 논의되고 있는 문제들
3. 선택한 가치관({value_context.rstrip(', ')})을 반영한 이슈
4. 각 이슈는 90자 이내로 구체적이고 상세하게 표현
5. 고등학생이 탐구 주제로 다룰 수 있는 현실적인 내용
6. 이전에 제시된 이슈와 완전히 다른 새로운 관점의 이슈

**응답 형식**: 
1. 이슈1 (90자 이내, 구체적 설명 포함)
2. 이슈2 (90자 이내, 구체적 설명 포함)
3. 이슈3 (90자 이내, 구체적 설명 포함)
4. 이슈4 (90자 이내, 구체적 설명 포함)
5. 이슈5 (90자 이내, 구체적 설명 포함)
"""

    try:
        response = llm.invoke(prompt)
        generated_text = response.content
        
        # 응답에서 이슈 추출
        issues = []
        for line in generated_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # 번호나 하이픈 제거하고 이슈 추출
                issue = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                if issue and len(issue) > 10:  # 최소 길이 증가
                    # 90자 이내로 자르기
                    if len(issue) > 90:
                        issue = issue[:90] + "..."
                    issues.append(issue)
        
        # 5개가 아닌 경우 기본값 추가
        if len(issues) < 5:
            default_issues = [
                f"{career} 분야의 국제 경쟁력 강화 필요성",
                f"{career} 업계의 지속가능한 발전 방안",
                f"{career} 전문가들의 역량 개발 과제",
                f"{career} 분야의 사회적 책임 강화",
                f"{career} 업무 환경 개선 필요성"
            ]
            issues.extend(default_issues[:5-len(issues)])
        
        return issues[:5]
        
    except Exception as e:
        print(f"이슈 생성 중 오류: {e}")
        # 기본 이슈 반환
        return [
            f"{career} 분야의 경쟁력 강화 필요",
            "기술 변화에 대한 적응 과제",
            "전문성 개발 요구 증가",
            "워라밸 개선 필요",
            "미래 시장 변화 대응"
        ]

def select_career_issues(career: str, career_values: list) -> list[str]:
    """직업 관련 이슈 선택받기 (다시 선택 기능 포함)"""
    all_generated_issues = []  # 지금까지 생성된 모든 이슈를 추적
    
    while True:
        print(f"\n🎯 3단계: '{career}' 직업과 관련하여 탐구해볼 만한 이슈들입니다.")
        print("🤖 AI가 선택한 가치관을 바탕으로 맞춤형 이슈를 생성했습니다.")
        
        # 현재 상태 요약 출력
        print(f"\n📋 현재 선택 정보:")
        print(f"   직업: {career}")
        print(f"   가치관: {', '.join([v.split(' - ')[0].split('. ')[1] for v in career_values])}")
        
        # AI로 이슈 생성 (이전 이슈들과 중복 방지)
        issues = generate_career_issues(career, career_values, all_generated_issues)
        
        # 현재 생성된 이슈들을 전체 목록에 추가
        all_generated_issues.extend(issues)
        
        print(f"\n📝 현재 이슈 목록:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        
        while True:
            print(f"\n선택 옵션:")
            print(f"1-5. 관심 있는 이슈 번호 선택 (예: 1,3,5)")
            print(f"0. 🔄 새로운 이슈 5개 다시 생성하기")
            
            selection = input("\n입력: ").strip()
            
            if selection == "0":
                print("\n🔄 새로운 이슈를 생성하고 있습니다...")
                break  # 외부 while 루프로 돌아가서 새 이슈 생성
            
            if not selection:
                print("번호를 입력해주세요!")
                continue
                
            try:
                selected_numbers = [int(num.strip()) for num in selection.split(',')]
                selected_issues = []
                
                for num in selected_numbers:
                    if 1 <= num <= len(issues):
                        selected_issues.append(issues[num-1])
                    else:
                        print(f"'{num}'은 유효하지 않은 번호입니다. 1-{len(issues)} 사이의 번호를 입력해주세요.")
                        break
                else:
                    if selected_issues:
                        print(f"\n🎯 선택한 이슈:")
                        for i, issue in enumerate(selected_issues, 1):
                            print(f"  {i}. {issue}")
                        
                        # 확인 및 다시선택 옵션
                        while True:
                            choice = input("\n1. 이 이슈들로 상담 진행하기\n2. 이슈 다시 선택하기\n선택 (1/2): ").strip()
                            
                            if choice == "1":
                                return selected_issues
                            elif choice == "2":
                                print("\n🔄 이슈를 다시 선택하겠습니다.\n")
                                break
                            else:
                                print("1 또는 2를 입력해주세요.")
                        break
                        
            except ValueError:
                print("숫자로 입력해주세요. (예: 1,3,5 또는 0)")

def career_counselor_node(state: State):
    """진로 상담사 노드"""
    messages = state["messages"]
    career = state.get("career", "")
    career_values = state.get("career_values", [])
    career_issues = state.get("career_issues", [])
    
    # 맞춤형 시스템 프롬프트 생성
    if career or career_values or career_issues:
        system_prompt = get_job_specific_prompt(career, career_values, career_issues)
    else:
        system_prompt = CAREER_COUNSELOR_PROMPT
    
    # 시스템 메시지가 없다면 추가
    if not messages or not isinstance(messages[0], SystemMessage):
        system_message = SystemMessage(content=system_prompt)
        messages = [system_message] + messages
    
    # LLM 응답 생성
    response = llm.invoke(messages)
    
    return {"messages": [response]}

# 그래프 생성
def create_career_counselor_agent():
    """진로 상담 에이전트 생성"""
    workflow = StateGraph(State)
    
    # 노드 추가
    workflow.add_node("counselor", career_counselor_node)
    
    # 엣지 설정
    workflow.add_edge(START, "counselor")
    workflow.add_edge("counselor", END)
    
    # 그래프 컴파일
    app = workflow.compile()
    return app

# 상담 세션 실행 함수
def start_counseling_session():
    """진로 상담 세션 시작"""
    print("🎓 안녕하세요! 고등학생 진로 상담사입니다.")
    print("여러분의 꿈과 진로에 대해 함께 이야기해보겠습니다.\n")
    
    # 1단계: 희망 직업 입력 (다시선택 기능 포함)
    career = get_desired_job()
    
    # 2단계: 가치관 선택 (다시선택 기능 포함)
    career_values = get_career_values(career)
    
    # 3단계: 관련 이슈 선택 (다시선택 기능 포함)
    career_issues = select_career_issues(career, career_values)
    
    # 에이전트 생성
    agent = create_career_counselor_agent()
    
    print("\n" + "="*60)
    print("🎉 모든 단계가 완료되었습니다!")
    print(f"📊 최종 선택 정보:")
    print(f"   직업: {career}")
    print(f"   가치관: {', '.join([v.split(' - ')[0].split('. ')[1] for v in career_values])}")
    print(f"   관심 이슈: {len(career_issues)}개 선택")
    print("\n💬 이제 자유롭게 질문하거나 고민을 말씀해주세요!")
    print("대화를 종료하려면 'quit' 또는 '종료'를 입력하세요.")
    print("="*60 + "\n")
    
    # 초기 상태 설정
    messages = []
    state = {
        "messages": messages, 
        "career": career,
        "career_values": career_values,
        "career_issues": career_issues
    }
    
    # 첫 인사말 생성
    initial_message = HumanMessage(
        content=f"안녕하세요! 저는 {career}가 되고 싶은 고등학생입니다. "
                f"제가 중요하게 생각하는 가치관은 {', '.join([v.split(' - ')[0].split('. ')[1] for v in career_values])}이고, "
                f"특히 {', '.join(career_issues)} 같은 이슈들에 관심이 있어요. 상담받고 싶습니다."
    )
    state["messages"].append(initial_message)
    
    try:
        # 첫 상담 메시지 생성
        result = agent.invoke(state)
        assistant_message = result["messages"][-1]
        print(f"상담사: {assistant_message.content}\n")
        messages.append(assistant_message)
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        return
    
    # 대화 진행
    while True:
        # 사용자 입력
        user_input = input("학생: ").strip()
        
        # 종료 조건
        if user_input.lower() in ['quit', '종료', 'exit', '그만']:
            print(f"\n상담사: {career}의 꿈을 향해 열심히 준비하세요! 선택한 가치관을 잊지 말고, 관심 있는 이슈들에 대해서도 계속 탐구해보세요. 언제든지 다시 찾아오세요! 화이팅! 🌟")
            break
        
        if not user_input:
            continue
        
        # 사용자 메시지 추가
        messages.append(HumanMessage(content=user_input))
        
        try:
            # 상태 업데이트
            state["messages"] = messages
            
            # 에이전트 실행
            result = agent.invoke(state)
            
            # 응답 출력
            assistant_message = result["messages"][-1]
            print(f"\n상담사: {assistant_message.content}\n")
            
            # 메시지 히스토리에 추가
            messages.append(assistant_message)
            
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
            print("다시 시도해주세요.\n")

if __name__ == "__main__":
    start_counseling_session()