#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 이슈 중복도 테스트 스크립트
"""

import requests
import json
import random
from collections import Counter
import difflib
from datetime import datetime

# 테스트용 데이터
TEST_CAREERS = [
    "의사", "교사", "개발자", "디자이너", "변호사", 
    "간호사", "공무원", "엔지니어", "마케터", "상담사"
]

TEST_VALUES = [
    ["경제적 가치 - 높은 수입, 안정적인 직업"],
    ["사회적 가치 - 사회에 긍정적인 영향, 봉사"],
    ["공동체적 가치 - 사람들과 협력, 소통"],
    ["능력 발휘 - 나의 재능과 역량을 최대한 발휘"],
    ["자율·창의성 - 독립적으로 일하고 새로운 아이디어 창출"],
    ["미래 비전 - 성장 가능성, 혁신적인 분야"]
]

def calculate_similarity(text1, text2):
    """두 텍스트 간 유사도 계산"""
    # 단어 기반 유사도
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    jaccard = len(intersection) / len(union)
    
    # 시퀀스 유사도
    sequence = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    return (jaccard + sequence) / 2

def run_single_test(test_id, base_url="http://localhost:8001"):
    """단일 테스트 실행"""
    print(f"🧪 테스트 {test_id} 시작...")
    
    career = random.choice(TEST_CAREERS)
    values = random.choice(TEST_VALUES)
    session_id = f"test_{test_id}_{datetime.now().strftime('%H%M%S')}"
    
    headers = {
        'Content-Type': 'application/json',
        'session-id': session_id
    }
    
    try:
        # 1단계: 직업 설정
        response = requests.post(
            f"{base_url}/api/career",
            headers=headers,
            json={"career": career},
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Career API failed: {response.status_code}")
        print(f"  ✅ 1단계: {career}")
        
        # 2단계: 가치관 설정
        response = requests.post(
            f"{base_url}/api/values",
            headers=headers,
            json={"values": values},
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Values API failed: {response.status_code}")
        print(f"  ✅ 2단계: {len(values)}개 가치관")
        
        # 3단계: 이슈 생성 (3번 반복)
        all_issues = []
        for round_num in range(3):
            response = requests.post(
                f"{base_url}/api/generate-issues",
                headers=headers,
                timeout=30
            )
            if response.status_code != 200:
                raise Exception(f"Generate issues API failed: {response.status_code}")
            
            data = response.json()
            issues = data.get('issues', [])
            all_issues.extend(issues)
            print(f"  📋 3단계-{round_num+1}: {len(issues)}개 이슈 생성")
        
        return {
            'test_id': test_id,
            'career': career,
            'values': values,
            'issues': all_issues,
            'success': True
        }
        
    except Exception as e:
        print(f"  ❌ 테스트 {test_id} 실패: {e}")
        return {
            'test_id': test_id,
            'career': career,
            'values': values,
            'issues': [],
            'success': False,
            'error': str(e)
        }

def analyze_duplicates(all_issues, threshold=0.7):
    """중복 이슈 분석"""
    duplicates = []
    processed = set()
    
    for i, issue1 in enumerate(all_issues):
        if i in processed:
            continue
            
        similar_group = [issue1]
        similar_indices = [i]
        
        for j, issue2 in enumerate(all_issues[i+1:], i+1):
            if j in processed:
                continue
                
            similarity = calculate_similarity(issue1, issue2)
            if similarity >= threshold:
                similar_group.append(issue2)
                similar_indices.append(j)
                processed.add(j)
        
        if len(similar_group) > 1:
            duplicates.append({
                'group': similar_group,
                'count': len(similar_group)
            })
            
        processed.add(i)
    
    total_duplicates = sum(group['count'] for group in duplicates)
    duplication_rate = total_duplicates / len(all_issues) if all_issues else 0
    
    return duplicates, duplication_rate

def main():
    print("🎯 AI 진로 상담 이슈 중복도 테스트 시작")
    print("=" * 60)
    
    # 10번 테스트 실행
    results = []
    all_issues = []
    
    for i in range(1, 11):
        result = run_single_test(i)
        results.append(result)
        
        if result['success']:
            all_issues.extend(result['issues'])
        
        print()
    
    # 결과 분석
    print("🔍 분석 결과:")
    print("=" * 60)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"📊 전체 통계:")
    print(f"  - 성공한 테스트: {len(successful_tests)}/10")
    print(f"  - 실패한 테스트: {len(failed_tests)}/10")
    print(f"  - 총 생성된 이슈 수: {len(all_issues)}")
    
    if not all_issues:
        print("❌ 분석할 이슈가 없습니다.")
        return
    
    # 중복도 분석
    duplicates, duplication_rate = analyze_duplicates(all_issues)
    
    print(f"  - 중복 그룹 수: {len(duplicates)}")
    print(f"  - 중복률: {duplication_rate:.2%}")
    print()
    
    # 중복률 평가
    if duplication_rate > 0.3:
        print("⚠️  경고: 중복률이 높습니다! (30% 이상)")
        print("   프롬프트 개선이 필요합니다.")
    elif duplication_rate > 0.15:
        print("⚡ 주의: 중복률이 다소 높습니다. (15% 이상)")
        print("   프롬프트 검토를 권장합니다.")
    else:
        print("✅ 양호: 중복률이 적절합니다.")
    
    print()
    
    # 주요 중복 그룹 표시
    if duplicates:
        print("📋 주요 중복 그룹 (상위 5개):")
        for i, group in enumerate(duplicates[:5], 1):
            print(f"  {i}. 중복 수: {group['count']}")
            for issue in group['group'][:2]:  # 최대 2개만 표시
                print(f"     - {issue}")
            if len(group['group']) > 2:
                print(f"     - ... 및 {len(group['group'])-2}개 더")
            print()
    
    # 직업별 분석
    career_issues = {}
    for result in successful_tests:
        career = result['career']
        if career not in career_issues:
            career_issues[career] = []
        career_issues[career].extend(result['issues'])
    
    print("🎯 직업별 분석:")
    for career, issues in career_issues.items():
        unique_issues = len(set(issues))
        career_duplication_rate = 1 - (unique_issues / len(issues)) if issues else 0
        print(f"  📌 {career}: 총 {len(issues)}개, 고유 {unique_issues}개, 중복률 {career_duplication_rate:.2%}")
    
    print()
    
    # 가장 빈번한 이슈들
    issue_counter = Counter(all_issues)
    most_common = issue_counter.most_common(10)
    
    print("🔥 가장 빈번한 이슈들:")
    for i, (issue, count) in enumerate(most_common, 1):
        if count > 1:
            print(f"  {i}. ({count}회) {issue}")
    
    print()
    print("=" * 60)
    
    # 프롬프트 개선 제안
    if duplication_rate > 0.2:
        print("🔧 프롬프트 개선 제안:")
        print("   1. 더 구체적인 업계/분야별 키워드 추가")
        print("   2. '이전 이슈와 완전히 다른' 조건 강화") 
        print("   3. 더 다양한 관점(기술, 사회, 경제, 환경 등) 요구")
        print("   4. 창의적이고 독창적인 이슈 생성 요청 강화")
        print("   5. 이슈별 세부 맥락과 배경 설명 요구")

if __name__ == "__main__":
    main()