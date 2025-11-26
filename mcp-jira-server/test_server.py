"""
SSG Jira MCP Server 테스트 스크립트
"""

import asyncio
import json
import sys
import os

# 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, os.path.dirname(__file__))

async def test_server():
    """서버 기본 기능을 테스트합니다."""
    print("=" * 60)
    print("🧪 SSG Jira MCP Server 테스트 시작")
    print("=" * 60)
    
    try:
        # 모듈 import 테스트
        print("\n📦 1. 필요한 모듈들 import 테스트...")
        
        try:
            import httpx
            print("  ✅ httpx 모듈 로드 성공")
        except ImportError as e:
            print(f"  ❌ httpx 모듈이 없습니다: {e}")
            print("     해결: pip install httpx")
            return False
        
        try:
            import mcp.server
            import mcp.types
            print("  ✅ mcp 모듈 로드 성공")
        except ImportError as e:
            print(f"  ❌ mcp 모듈이 없습니다: {e}")
            print("     해결: pip install mcp")
            return False
        
        # 서버 클래스 import 테스트
        print("\n🔧 2. 서버 클래스 로드 테스트...")
        try:
            from ssg_jira_mcp_server import SSGJiraMCPServer
            print("  ✅ SSGJiraMCPServer 클래스 로드 성공")
        except Exception as e:
            print(f"  ❌ 서버 클래스 로드 실패: {e}")
            return False
        
        # 서버 인스턴스 생성 테스트
        print("\n⚙️ 3. 서버 인스턴스 생성 테스트...")
        try:
            server = SSGJiraMCPServer()
            print("  ✅ 서버 인스턴스 생성 성공")
        except Exception as e:
            print(f"  ❌ 서버 인스턴스 생성 실패: {e}")
            return False
        
        # 기본 설정 확인
        print("\n📋 4. 서버 기본 설정 확인...")
        print(f"  - 서버 이름: {server.server.name}")
        print(f"  - Jira URL: {server.base_url}")
        print(f"  - 인증 상태: {'✅ 설정됨' if server.headers else '⚠️ 미설정'}")
        if server.username:
            print(f"  - 사용자명: {server.username}")
        
        # 환경 변수 확인
        print("\n🔐 5. 환경 변수 확인...")
        jira_username = os.getenv("JIRA_USERNAME")
        jira_token = os.getenv("JIRA_API_TOKEN")
        
        if jira_username:
            print(f"  ✅ JIRA_USERNAME: {jira_username}")
        else:
            print("  ⚠️ JIRA_USERNAME 환경 변수가 설정되지 않았습니다")
        
        if jira_token:
            print(f"  ✅ JIRA_API_TOKEN: {'*' * len(jira_token)}")
        else:
            print("  ⚠️ JIRA_API_TOKEN 환경 변수가 설정되지 않았습니다")
        
        # 도구 정의 확인
        print("\n🛠️ 6. 도구 정의 확인...")
        expected_tools = [
            "get_project", 
            "search_issues",
            "get_issue",
            "get_project_versions",
            "search_qa_issues"
        ]
        
        print(f"  📋 예상되는 도구 목록 ({len(expected_tools)}개):")
        for tool in expected_tools:
            print(f"    - {tool}")
        
        # 인증 검증 테스트
        print("\n🔑 7. 인증 검증 테스트...")
        try:
            await server._check_auth()
            print("  ✅ 인증 검증 통과")
        except ValueError as e:
            if "인증 정보가 설정되지 않았습니다" in str(e):
                print("  ⚠️ 인증 정보가 설정되지 않았습니다")
                print("     - Claude Desktop 설정에서 환경 변수를 확인하세요")
            else:
                print(f"  ❌ 예상과 다른 에러: {str(e)}")
        except Exception as e:
            print(f"  ❌ 예상과 다른 에러 타입: {type(e).__name__}: {str(e)}")
        
        # API 연결 테스트 (인증 정보가 있는 경우)
        if server.headers:
            print("\n🌐 8. Jira API 연결 테스트...")
            try:
                # 간단한 프로젝트 조회 테스트
                result = await server._get_project({"project_key": "QAQ"})
                if result and "프로젝트 정보" in result[0].text:
                    print("  ✅ Jira API 연결 성공")
                    print("  ✅ QAQ 프로젝트 조회 성공")
                else:
                    print("  ⚠️ 예상과 다른 응답 형식")
            except Exception as e:
                print(f"  ❌ API 연결 실패: {str(e)}")
                print("     - 네트워크 연결을 확인하세요")
                print("     - Jira URL이 올바른지 확인하세요")
                print("     - 인증 정보가 올바른지 확인하세요")
        
        print("\n" + "=" * 60)
        print("🎉 기본 테스트 완료!")
        print("=" * 60)
        
        if server.headers:
            print("\n✅ 서버가 정상적으로 작동할 준비가 되었습니다!")
            print("\n📌 다음 단계:")
            print("  1. Claude Desktop을 재시작하세요")
            print("  2. Claude에서 Jira 도구를 사용할 수 있습니다")
        else:
            print("\n⚠️ 인증 정보를 설정해야 합니다!")
            print("\n📌 설정 방법:")
            print("  1. Claude Desktop 설정 파일 확인")
            print("  2. env 섹션에 JIRA_USERNAME, JIRA_API_TOKEN 설정")
            print("  3. Claude Desktop 재시작")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 테스트 중 오류 발생: {type(e).__name__}")
        print(f"   {str(e)}")
        print("=" * 60)
        print("\n🔧 해결 방법:")
        print("  1. 필요한 패키지 설치: pip install -r requirements.txt")
        print("  2. Python 버전 확인 (3.8 이상 권장)")
        print("  3. 파일 경로 및 권한 확인")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
