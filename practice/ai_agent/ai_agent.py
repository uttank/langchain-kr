from typing import Annotated, TypedDict, List, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uuid
import json

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(title="고등학생 진로 상담 AI", description="AI를 활용한 고등학생 진로 상담 서비스")

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

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

# Pydantic 모델 정의
class CareerRequest(BaseModel):
    career: str

class ValuesRequest(BaseModel):
    values: List[str]

class IssuesRequest(BaseModel):
    issues: List[str]

class ChatRequest(BaseModel):
    message: str

class SessionData(BaseModel):
    career: str = ""
    career_values: List[str] = []
    career_issues: List[str] = []
    messages: List = []
    agent: Optional[object] = None
    previous_issues: List[str] = []

# 세션별 상태 저장
user_sessions = {}

def generate_career_issues(career: str, career_values: list, previous_issues: Optional[list] = None) -> list:
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
        for line in str(generated_text).split('\n'):
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

# 세션 헬퍼 함수
def get_session_id(request: Request) -> str:
    """세션 ID 가져오기 또는 생성"""
    session_id = request.headers.get("session-id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

def get_or_create_session(session_id: str) -> dict:
    """세션 가져오기 또는 생성"""
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            'career': '',
            'career_values': [],
            'career_issues': [],
            'messages': [],
            'agent': None,
            'previous_issues': []
        }
    return user_sessions[session_id]

# 라우트 정의
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/career")
async def set_career(request: Request, career_request: CareerRequest):
    """직업 설정"""
    career = career_request.career.strip()
    
    if not career:
        raise HTTPException(status_code=400, detail="직업을 입력해주세요.")
    
    session_id = get_session_id(request)
    user_session = get_or_create_session(session_id)
    user_session['career'] = career
    
    return {"success": True, "career": career, "session_id": session_id}

@app.post("/api/values")
async def set_values(request: Request, values_request: ValuesRequest):
    """가치관 설정"""
    values = values_request.values
    
    if not values:
        raise HTTPException(status_code=400, detail="최소 하나의 가치관을 선택해주세요.")
    
    session_id = get_session_id(request)
    if session_id not in user_sessions:
        raise HTTPException(status_code=400, detail="세션이 유효하지 않습니다.")
    
    user_sessions[session_id]['career_values'] = values
    
    return {"success": True, "values": values}

@app.post("/api/generate-issues")
async def generate_issues(request: Request):
    """이슈 생성"""
    session_id = get_session_id(request)
    if session_id not in user_sessions:
        raise HTTPException(status_code=400, detail="세션이 유효하지 않습니다.")
    
    user_session = user_sessions[session_id]
    career = user_session.get('career', '')
    career_values = user_session.get('career_values', [])
    
    if not career:
        raise HTTPException(status_code=400, detail="직업을 먼저 설정해주세요.")
    
    # 이전에 생성된 이슈들 가져오기
    previous_issues = user_session.get('previous_issues', [])
    
    # 새로운 이슈 생성
    issues = generate_career_issues(career, career_values, previous_issues)
    
    # 생성된 이슈를 이전 이슈 목록에 추가
    user_session['previous_issues'] = previous_issues + issues
    
    return {"success": True, "issues": issues}

@app.post("/api/issues")
async def set_issues(request: Request, issues_request: IssuesRequest):
    """이슈 설정"""
    issues = issues_request.issues
    
    if not issues:
        raise HTTPException(status_code=400, detail="최소 하나의 이슈를 선택해주세요.")
    
    session_id = get_session_id(request)
    if session_id not in user_sessions:
        raise HTTPException(status_code=400, detail="세션이 유효하지 않습니다.")
    
    user_sessions[session_id]['career_issues'] = issues
    
    # 에이전트 생성 및 초기 메시지 설정
    agent = create_career_counselor_agent()
    user_sessions[session_id]['agent'] = agent
    
    # 초기 상담 메시지 생성
    user_session = user_sessions[session_id]
    career = user_session['career']
    career_values = user_session['career_values']
    career_issues = user_session['career_issues']
    
    initial_message = HumanMessage(
        content=f"안녕하세요! 저는 {career}가 되고 싶은 고등학생입니다. "
                f"제가 중요하게 생각하는 가치관은 {', '.join([v.split(' - ')[0].split('. ')[1] if ' - ' in v else v.split('. ')[1] if '. ' in v else v for v in career_values])}이고, "
                f"특히 {', '.join(career_issues)} 같은 이슈들에 관심이 있어요. 상담받고 싶습니다."
    )
    
    state = {
        "messages": [initial_message], 
        "career": career,
        "career_values": career_values,
        "career_issues": career_issues
    }
    
    try:
        # 첫 상담 메시지 생성
        result = agent.invoke(state)
        assistant_message = result["messages"][-1]
        
        user_sessions[session_id]['messages'] = [initial_message, assistant_message]
        
        return {
            "success": True, 
            "issues": issues,
            "initial_message": assistant_message.content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상담 초기화 중 오류: {str(e)}")

@app.post("/api/chat")
async def chat(request: Request, chat_request: ChatRequest):
    """채팅"""
    message = chat_request.message.strip()
    
    if not message:
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")
    
    session_id = get_session_id(request)
    if session_id not in user_sessions:
        raise HTTPException(status_code=400, detail="세션이 유효하지 않습니다.")
    
    user_session = user_sessions[session_id]
    agent = user_session.get('agent')
    
    if not agent:
        raise HTTPException(status_code=400, detail="상담이 초기화되지 않았습니다. 설정을 완료해주세요.")
    
    # 사용자 메시지 추가
    user_message = HumanMessage(content=message)
    user_session['messages'].append(user_message)
    
    try:
        # 상태 업데이트
        state = {
            "messages": user_session['messages'],
            "career": user_session['career'],
            "career_values": user_session['career_values'],
            "career_issues": user_session['career_issues']
        }
        
        # 에이전트 실행
        result = agent.invoke(state)
        
        # 응답 메시지
        assistant_message = result["messages"][-1]
        user_session['messages'].append(assistant_message)
        
        return {
            "success": True,
            "response": assistant_message.content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상담 중 오류: {str(e)}")

@app.post("/api/reset")
async def reset_session(request: Request):
    """세션 초기화"""
    session_id = get_session_id(request)
    if session_id in user_sessions:
        del user_sessions[session_id]
    
    new_session_id = str(uuid.uuid4())
    return {"success": True, "session_id": new_session_id}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)