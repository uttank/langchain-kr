#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹검색 기능이 추가된 AI 진로 상담 시스템 테스트
"""

import requests
import json
import random
from collections import Counter
import difflib
from datetime import datetime

# 테스트용 데이터
TEST_CAREERS = [
    "개발자", "디자이너", "마케터"  # 테스트 시간 단축을 위해 3개만
]

TEST_VALUES = [
    ["경제적 가치 - 높은 수입, 안정적인 직업"],
    ["능력 발휘 - 전문성과 역량을 발휘하고 성장할 수 있는 일"],
    ["미래 비전 - 미래 성장 가능성이 높고 혁신적인 일"]
]

def run_single_test_with_search(test_id, base_url="http://localhost:8002"):
    """웹검색 기능이 포함된 단일 테스트 실행"""
    print(f"🧪 테스트 {test_id} 시작...")
    
    try:
        # 세션 시작
        session_response = requests.post(f"{base_url}/api/start")
        if session_response.status_code != 200:
            return None, f"세션 시작 실패: {session_response.status_code}"
        
        session_id = session_response.json()["session_id"]
        headers = {"X-Session-ID": session_id}
        
        # 1단계: 직업 선택
        career = random.choice(TEST_CAREERS)
        career_response = requests.post(
            f"{base_url}/api/career",
            json={"career": career},
            headers=headers
        )
        
        if career_response.status_code != 200:
            return None, f"1단계 실패: {career_response.status_code}"
        
        print(f"  ✅ 1단계: {career}")
        
        # 2단계: 가치관 선택
        values = random.choice(TEST_VALUES)
        values_response = requests.post(
            f"{base_url}/api/values",
            json={"career_values": values},
            headers=headers
        )
        
        if values_response.status_code != 200:
            return None, f"2단계 실패: {values_response.status_code}"
        
        print(f"  ✅ 2단계: {len(values)}개 가치관")
        
        # 3단계: 이슈 생성 (웹검색 포함)
        all_issues = []
        for i in range(3):
            print(f"  🔍 3단계-{i+1}: 웹검색 포함 이슈 생성 중...")
            issues_response = requests.post(
                f"{base_url}/api/issues",
                json={"career": career, "career_values": values},
                headers=headers
            )
            
            if issues_response.status_code != 200:
                return None, f"3단계-{i+1} 실패: {issues_response.status_code}"
            
            issues = issues_response.json().get("issues", [])
            all_issues.extend(issues)
            print(f"  📋 3단계-{i+1}: {len(issues)}개 이슈 생성")
        
        return {
            "career": career,
            "values": values,
            "issues": all_issues,
            "test_id": test_id
        }, None
        
    except Exception as e:
        return None, f"테스트 {test_id} 실패: {str(e)}"

def analyze_search_enhanced_results(results):
    """웹검색 기능이 추가된 결과 분석"""
    print("🔍 웹검색 강화 시스템 분석 결과:")
    print("=" * 60)
    
    if not results:
        print("❌ 분석할 결과가 없습니다.")
        return
    
    # 전체 이슈 수집
    all_issues = []
    career_issues = {}
    
    for result in results:
        career = result["career"]
        issues = result["issues"]
        all_issues.extend(issues)
        
        if career not in career_issues:
            career_issues[career] = []
        career_issues[career].extend(issues)
    
    # 중복도 분석
    issue_counts = Counter(all_issues)
    total_issues = len(all_issues)
    unique_issues = len(set(all_issues))
    duplicate_groups = {issue: count for issue, count in issue_counts.items() if count > 1}
    
    print(f"📊 전체 통계:")
    print(f"  - 성공한 테스트: {len(results)}/3")
    print(f"  - 총 생성된 이슈 수: {total_issues}")
    print(f"  - 고유 이슈 수: {unique_issues}")
    print(f"  - 중복 그룹 수: {len(duplicate_groups)}")
    
    if total_issues > 0:
        duplication_rate = (total_issues - unique_issues) / total_issues * 100
        print(f"  - 중복률: {duplication_rate:.2f}%")
        
        if duplication_rate < 10:
            print("✅ 우수: 웹검색 기능이 다양성을 크게 향상시켰습니다!")
        elif duplication_rate < 30:
            print("⚠️  양호: 웹검색 기능이 도움되고 있습니다.")
        else:
            print("❌ 개선 필요: 웹검색 기능 최적화가 필요합니다.")
    
    # 직업별 분석
    print(f"\n🎯 직업별 분석:")
    for career, issues in career_issues.items():
        career_unique = len(set(issues))
        career_total = len(issues)
        career_dup_rate = (career_total - career_unique) / career_total * 100 if career_total > 0 else 0
        print(f"  📌 {career}: 총 {career_total}개, 고유 {career_unique}개, 중복률 {career_dup_rate:.2f}%")
    
    # 웹검색 품질 평가
    print(f"\n🌐 웹검색 품질 지표:")
    
    # 최신성 키워드 분석
    current_keywords = ["2024", "2025", "최근", "현재", "트렌드", "AI", "디지털", "변화"]
    current_issue_count = sum(1 for issue in all_issues if any(keyword in issue for keyword in current_keywords))
    print(f"  - 최신성 반영 이슈: {current_issue_count}/{total_issues}개 ({current_issue_count/total_issues*100:.1f}%)")
    
    # 구체성 분석 (긴 이슈 = 더 구체적)
    detailed_issues = [issue for issue in all_issues if len(issue) > 50]
    print(f"  - 구체적 이슈 (50자 이상): {len(detailed_issues)}/{total_issues}개 ({len(detailed_issues)/total_issues*100:.1f}%)")
    
    print(f"\n🔥 가장 빈번한 이슈들:")
    for issue, count in issue_counts.most_common(5):
        print(f"  {count}회: {issue}")

def main():
    """웹검색 기능 테스트 메인 함수"""
    print("🎯 웹검색 강화 AI 진로 상담 시스템 테스트")
    print("=" * 60)
    
    # 3번의 테스트 실행 (시간 단축)
    results = []
    errors = []
    
    for i in range(1, 4):
        result, error = run_single_test_with_search(i)
        if result:
            results.append(result)
        else:
            errors.append(error)
    
    # 결과 분석
    analyze_search_enhanced_results(results)
    
    if errors:
        print(f"\n❌ 오류 발생:")
        for error in errors:
            print(f"  - {error}")

if __name__ == "__main__":
    main()