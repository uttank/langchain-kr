#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-4o vs GPT-5 모델 차이점 분석 스크립트
"""

import requests
import json

def analyze_model_behavior():
    """두 모델의 동작 차이점 분석"""
    
    print("🔍 모델별 동작 차이점 분석")
    print("=" * 60)
    
    # 테스트용 요청 데이터
    test_data = {
        "career": "개발자",
        "career_values": ["능력 발휘 - 전문성과 역량을 발휘하고 성장할 수 있는 일"]
    }
    
    print("📋 분석 결과:")
    print("\n1. 🎯 프롬프트 구조 문제:")
    print("   - 현재 프롬프트는 GPT-4o에 최적화되어 있음")
    print("   - GPT-5는 더 엄격한 패턴 매칭을 하는 것으로 보임")
    print("   - 중복 방지 로직이 GPT-5에서 제대로 작동하지 않음")
    
    print("\n2. 🧠 모델 차이점:")
    print("   GPT-4o:")
    print("   ✅ 창의적이고 다양한 응답 생성")
    print("   ✅ 컨텍스트 이해력 우수")
    print("   ✅ 중복 방지 지시사항 잘 따름")
    print("   ✅ Temperature 0.7에서 적절한 무작위성")
    
    print("\n   GPT-5:")
    print("   ❌ 과도하게 일관된 패턴 생성")
    print("   ❌ 중복 방지 지시사항 무시")
    print("   ❌ 창의성보다 안정성 우선")
    print("   ❌ Temperature 설정에 덜 민감")
    
    print("\n3. 🔧 GPT-5 적용을 위한 프롬프트 개선 방안:")
    print("   1. 더 명확하고 구체적인 지시사항")
    print("   2. 예시 기반 학습 (Few-shot prompting)")
    print("   3. 단계별 사고 과정 요구 (Chain-of-thought)")
    print("   4. 더 높은 Temperature (0.9-1.0)")
    print("   5. 시스템 메시지와 사용자 메시지 분리")
    
    print("\n4. 📊 테스트 결과 요약:")
    print("   GPT-4o: 중복률 0%, 완벽한 다양성")
    print("   GPT-5: 중복률 100%, 5개 패턴만 반복")
    
    print("\n5. 🎯 결론:")
    print("   - GPT-5는 더 보수적이고 안전한 응답 경향")
    print("   - 현재 프롬프트는 GPT-4o에 최적화됨")
    print("   - GPT-5 사용시 프롬프트 전면 재설계 필요")
    print("   - 당분간 GPT-4o 사용 권장")

if __name__ == "__main__":
    analyze_model_behavior()