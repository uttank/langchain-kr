#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 진로 상담 자동 테스트 및 이슈 중복도 검사 도구
"""

import asyncio
import aiohttp
import json
import random
from typing import List, Dict, Set
from collections import Counter
import difflib
from datetime import datetime
import sys
import os

# 테스트용 데이터
TEST_CAREERS = [
    "의사", "교사", "개발자", "디자이너", "변호사", 
    "간호사", "공무원", "엔지니어", "마케터", "상담사",
    "기자", "예술가", "요리사", "경찰관", "소방관"
]

TEST_VALUES = [
    ["경제적 가치 - 높은 수입, 안정적인 직업"],
    ["사회적 가치 - 사회에 긍정적인 영향, 봉사"],
    ["공동체적 가치 - 사람들과 협력, 소통"],
    ["능력 발휘 - 나의 재능과 역량을 최대한 발휘"],
    ["자율·창의성 - 독립적으로 일하고 새로운 아이디어 창출"],
    ["미래 비전 - 성장 가능성, 혁신적인 분야"],
    ["경제적 가치 - 높은 수입, 안정적인 직업", "사회적 가치 - 사회에 긍정적인 영향, 봉사"],
    ["능력 발휘 - 나의 재능과 역량을 최대한 발휘", "자율·창의성 - 독립적으로 일하고 새로운 아이디어 창출"],
    ["미래 비전 - 성장 가능성, 혁신적인 분야", "공동체적 가치 - 사람들과 협력, 소통"]
]

class CareerTestRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_single_test(self, test_id: int) -> Dict:
        """단일 테스트 실행"""
        print(f"🧪 테스트 {test_id} 시작...")
        
        # 랜덤 데이터 선택
        career = random.choice(TEST_CAREERS)
        values = random.choice(TEST_VALUES)
        
        session_id = f"test_{test_id}_{datetime.now().strftime('%H%M%S')}"
        headers = {
            'Content-Type': 'application/json',
            'session-id': session_id
        }
        
        test_result = {
            'test_id': test_id,
            'session_id': session_id,
            'career': career,
            'values': values,
            'issues': [],
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 1단계: 직업 설정
            async with self.session.post(
                f"{self.base_url}/api/career",
                headers=headers,
                json={"career": career}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Career API failed: {response.status}")
                data = await response.json()
                print(f"  ✅ 1단계 완료: {career}")
            
            # 2단계: 가치관 설정
            async with self.session.post(
                f"{self.base_url}/api/values",
                headers=headers,
                json={"values": values}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Values API failed: {response.status}")
                data = await response.json()
                print(f"  ✅ 2단계 완료: {len(values)}개 가치관")
            
            # 3단계: 이슈 생성 (여러 번 반복)
            all_issues = []
            for round_num in range(3):  # 3번 이슈 생성
                async with self.session.post(
                    f"{self.base_url}/api/generate-issues",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Generate issues API failed: {response.status}")
                    data = await response.json()
                    issues = data.get('issues', [])
                    all_issues.extend(issues)
                    print(f"  📋 3단계-{round_num+1}: {len(issues)}개 이슈 생성")
            
            test_result['issues'] = all_issues
            print(f"  ✅ 테스트 {test_id} 완료: 총 {len(all_issues)}개 이슈")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ❌ 테스트 {test_id} 실패: {e}")
        
        return test_result
    
    async def run_tests(self, num_tests: int = 10) -> List[Dict]:
        """여러 테스트 실행"""
        print(f"🚀 {num_tests}개 테스트 시작...")
        
        tasks = []
        for i in range(1, num_tests + 1):
            task = self.run_single_test(i)
            tasks.append(task)
            # 서버 부하 방지를 위한 약간의 지연
            await asyncio.sleep(0.5)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'error': str(result),
                    'timestamp': datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        self.test_results = processed_results
        return processed_results

class IssueAnalyzer:
    def __init__(self, test_results: List[Dict]):
        self.test_results = test_results
        self.all_issues = []
        self.career_issues = {}
        
        # 이슈 데이터 정리
        self._organize_issues()
    
    def _organize_issues(self):
        """이슈 데이터 정리"""
        for result in self.test_results:
            if result.get('error'):
                continue
                
            career = result.get('career', '')
            issues = result.get('issues', [])
            
            # 전체 이슈 목록에 추가
            self.all_issues.extend(issues)
            
            # 직업별 이슈 분류
            if career not in self.career_issues:
                self.career_issues[career] = []
            self.career_issues[career].extend(issues)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간 유사도 계산 (0-1)"""
        # 간단한 단어 기반 유사도
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(intersection) / len(union)
        
        # difflib을 사용한 시퀀스 유사도도 함께 고려
        sequence_similarity = difflib.SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        
        # 두 유사도의 평균
        return (jaccard_similarity + sequence_similarity) / 2
    
    def find_duplicates(self, threshold: float = 0.7) -> Dict:
        """중복 이슈 찾기"""
        duplicates = []
        processed = set()
        
        for i, issue1 in enumerate(self.all_issues):
            if i in processed:
                continue
                
            similar_issues = [issue1]
            similar_indices = [i]
            
            for j, issue2 in enumerate(self.all_issues[i+1:], i+1):
                if j in processed:
                    continue
                    
                similarity = self.calculate_similarity(issue1, issue2)
                if similarity >= threshold:
                    similar_issues.append(issue2)
                    similar_indices.append(j)
                    processed.add(j)
            
            if len(similar_issues) > 1:
                duplicates.append({
                    'group': similar_issues,
                    'count': len(similar_issues),
                    'similarity_scores': [
                        self.calculate_similarity(issue1, issue) 
                        for issue in similar_issues[1:]
                    ]
                })
                
            processed.add(i)
        
        return {
            'duplicate_groups': duplicates,
            'total_duplicates': sum(group['count'] for group in duplicates),
            'total_issues': len(self.all_issues),
            'duplication_rate': sum(group['count'] for group in duplicates) / len(self.all_issues) if self.all_issues else 0
        }
    
    def analyze_by_career(self) -> Dict:
        """직업별 이슈 분석"""
        career_analysis = {}
        
        for career, issues in self.career_issues.items():
            if not issues:
                continue
                
            # 해당 직업의 이슈들만으로 중복도 검사
            career_duplicates = []
            processed = set()
            
            for i, issue1 in enumerate(issues):
                if i in processed:
                    continue
                    
                similar_issues = [issue1]
                for j, issue2 in enumerate(issues[i+1:], i+1):
                    if j in processed:
                        continue
                        
                    similarity = self.calculate_similarity(issue1, issue2)
                    if similarity >= 0.7:
                        similar_issues.append(issue2)
                        processed.add(j)
                
                if len(similar_issues) > 1:
                    career_duplicates.append(similar_issues)
                processed.add(i)
            
            career_analysis[career] = {
                'total_issues': len(issues),
                'unique_issues': len(set(issues)),
                'duplicate_groups': len(career_duplicates),
                'duplication_rate': 1 - (len(set(issues)) / len(issues)) if issues else 0,
                'most_common': Counter(issues).most_common(5)
            }
        
        return career_analysis
    
    def generate_report(self) -> str:
        """분석 보고서 생성"""
        duplicates = self.find_duplicates()
        career_analysis = self.analyze_by_career()
        
        report = []
        report.append("=" * 80)
        report.append("🔍 AI 진로 상담 이슈 중복도 분석 보고서")
        report.append("=" * 80)
        report.append(f"📊 전체 통계:")
        report.append(f"  - 총 테스트 수: {len(self.test_results)}")
        report.append(f"  - 총 생성된 이슈 수: {len(self.all_issues)}")
        report.append(f"  - 중복 이슈 그룹 수: {len(duplicates['duplicate_groups'])}")
        report.append(f"  - 중복률: {duplicates['duplication_rate']:.2%}")
        report.append("")
        
        if duplicates['duplication_rate'] > 0.3:  # 30% 이상
            report.append("⚠️  경고: 중복률이 높습니다! (30% 이상)")
            report.append("   프롬프트 개선이 필요합니다.")
        elif duplicates['duplication_rate'] > 0.15:  # 15% 이상
            report.append("⚡ 주의: 중복률이 다소 높습니다. (15% 이상)")
            report.append("   프롬프트 검토를 권장합니다.")
        else:
            report.append("✅ 양호: 중복률이 적절합니다.")
        
        report.append("")
        report.append("📋 주요 중복 그룹:")
        for i, group in enumerate(duplicates['duplicate_groups'][:5], 1):
            report.append(f"  {i}. 중복 수: {group['count']}")
            for issue in group['group'][:3]:  # 최대 3개만 표시
                report.append(f"     - {issue[:60]}...")
            report.append("")
        
        report.append("🎯 직업별 분석:")
        for career, analysis in career_analysis.items():
            report.append(f"  📌 {career}:")
            report.append(f"     총 이슈: {analysis['total_issues']}, "
                         f"고유 이슈: {analysis['unique_issues']}, "
                         f"중복률: {analysis['duplication_rate']:.2%}")
            
            if analysis['most_common']:
                report.append(f"     가장 빈번한 이슈: {analysis['most_common'][0][0][:40]}... ({analysis['most_common'][0][1]}회)")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

async def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 진로 상담 자동 테스트')
    parser.add_argument('--tests', '-t', type=int, default=10, help='테스트 실행 횟수 (기본: 10)')
    parser.add_argument('--url', '-u', default='http://localhost:8000', help='서버 URL (기본: http://localhost:8000)')
    parser.add_argument('--output', '-o', help='결과 저장 파일명')
    parser.add_argument('--threshold', type=float, default=0.7, help='중복 판정 임계값 (기본: 0.7)')
    
    args = parser.parse_args()
    
    print(f"🎯 AI 진로 상담 자동 테스트 시작")
    print(f"   - 테스트 횟수: {args.tests}")
    print(f"   - 서버 URL: {args.url}")
    print(f"   - 중복 임계값: {args.threshold}")
    print()
    
    # 테스트 실행
    async with CareerTestRunner(args.url) as runner:
        try:
            results = await runner.run_tests(args.tests)
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            return
    
    # 결과 분석
    print("\n🔍 결과 분석 중...")
    analyzer = IssueAnalyzer(results)
    report = analyzer.generate_report()
    
    # 결과 출력
    print(report)
    
    # 파일 저장
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
            f.write("\n\n" + "="*80 + "\n")
            f.write("📄 상세 테스트 결과:\n")
            f.write("="*80 + "\n")
            f.write(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"\n💾 결과가 '{args.output}' 파일에 저장되었습니다.")
    
    # 프롬프트 개선 제안
    duplication_rate = analyzer.find_duplicates(args.threshold)['duplication_rate']
    if duplication_rate > 0.3:
        print("\n🔧 프롬프트 개선 제안:")
        print("   1. 더 구체적인 업계/분야별 키워드 추가")
        print("   2. '이전 이슈와 완전히 다른' 조건 강화") 
        print("   3. 더 다양한 관점(기술, 사회, 경제, 환경 등) 요구")
        print("   4. 이슈 길이 제한 조정 (현재 90자)")
        print("   5. 더 창의적이고 독창적인 이슈 생성 요청")

if __name__ == "__main__":
    asyncio.run(main())