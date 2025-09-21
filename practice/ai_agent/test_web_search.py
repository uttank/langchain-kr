#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹검색 기능 단독 테스트
"""

import sys
sys.path.append('/Users/yhpark/work/langchain-kr/practice/ai_agent')

from ai_agent_search import generate_search_keywords, search_web_for_issues, extract_issues_from_search, generate_career_issues

def test_web_search_functionality():
    """웹검색 기능 단독 테스트"""
    print("🔍 웹검색 기능 단독 테스트")
    print("=" * 50)
    
    # 테스트 데이터
    career = "개발자"
    career_values = ["능력 발휘 - 전문성과 역량을 발휘하고 성장할 수 있는 일"]
    
    print(f"📋 테스트 대상: {career}")
    print(f"📋 가치관: {career_values[0]}")
    print()
    
    # 1단계: 검색 키워드 생성
    print("🎯 1단계: 검색 키워드 생성")
    keywords = generate_search_keywords(career, career_values)
    print(f"생성된 키워드: {keywords[:5]}...")  # 처음 5개만 표시
    print()
    
    # 2단계: 웹검색 실행
    print("🌐 2단계: 웹검색 실행")
    search_results = search_web_for_issues(keywords[:3], max_results=2)  # 시간 단축
    print(f"검색 결과 수: {len(search_results)}개")
    
    if search_results:
        print("검색 결과 샘플:")
        for i, result in enumerate(search_results[:2]):
            print(f"  {i+1}. {result['title'][:50]}...")
    print()
    
    # 3단계: 이슈 추출
    print("📝 3단계: 검색 결과에서 이슈 추출")
    web_issues = extract_issues_from_search(search_results, career)
    print(f"추출된 웹 이슈 수: {len(web_issues)}개")
    
    if web_issues:
        print("추출된 웹 이슈들:")
        for i, issue in enumerate(web_issues):
            print(f"  {i+1}. {issue}")
    print()
    
    # 4단계: 통합 이슈 생성
    print("🚀 4단계: 웹검색과 AI를 결합한 최종 이슈 생성")
    final_issues = generate_career_issues(career, career_values)
    print(f"최종 생성된 이슈 수: {len(final_issues)}개")
    
    if final_issues:
        print("최종 이슈들:")
        for i, issue in enumerate(final_issues):
            print(f"  {i+1}. {issue}")
    
    print()
    print("✅ 웹검색 기능 테스트 완료!")
    
    # 성능 평가
    print("\n📊 성능 평가:")
    print(f"  - 키워드 생성: {'✅' if keywords else '❌'}")
    print(f"  - 웹검색 실행: {'✅' if search_results else '❌'}")
    print(f"  - 이슈 추출: {'✅' if web_issues else '❌'}")
    print(f"  - 최종 이슈 생성: {'✅' if final_issues else '❌'}")
    
    if web_issues and final_issues:
        print(f"  - 웹검색 이슈 활용도: {len(web_issues)}개 발견")
        print("  - 전체 평가: ✅ 웹검색 기능 정상 작동")
    else:
        print("  - 전체 평가: ⚠️  일부 기능 개선 필요")

if __name__ == "__main__":
    test_web_search_functionality()