@echo off
chcp 65001 >nul
echo 🚀 SSG Jira MCP Server 설정 가이드 (환경 변수 인증 방식)
echo ================================================================

echo.
echo 📦 1. 필요한 패키지 설치 중...
pip install -r requirements.txt

echo.
echo 🔑 2. Jira API 토큰 생성
echo 1. SSG Jira 접속: https://project.ssgadm.com
echo 2. 프로필 → 계정 설정 → 보안 → API 토큰 생성
echo 3. 토큰 이름: "Claude MCP Server"
echo 4. 생성된 토큰 복사 및 저장

echo.
echo ⚙️ 3. Claude Desktop 설정
echo.
echo Claude Desktop 설정 파일 위치:
echo %%APPDATA%%\Claude\claude_desktop_config.json
echo.
echo 다음 내용을 설정 파일에 추가하세요:
echo {
echo   "mcpServers": {
echo     "ssg-jira": {
echo       "command": "python",
echo       "args": [
echo         "C:\\ssg\\claude\\mcp-jira-server\\ssg_jira_mcp_server.py"
echo       ],
echo       "env": {
echo         "JIRA_USERNAME": "your-email@ssg.com",
echo         "JIRA_API_TOKEN": "your-api-token-here"
echo       }
echo     }
echo   }
echo }

echo.
echo 🔄 4. Claude Desktop 재시작
echo Claude Desktop을 완전히 종료하고 다시 시작하세요.

echo.
echo 🎯 5. 사용법
echo Claude Desktop에서 다음과 같이 입력하세요:
echo "get_project 도구를 사용해서 QAQ 프로젝트 정보를 조회해줘."
echo "search_qa_issues 도구를 사용해서 진행중인 에픽들을 찾아줘."

echo.
echo ✅ 설정 완료! 이제 configure_auth 도구 없이 바로 사용 가능합니다.
echo.
echo 📋 사용 가능한 도구:
echo - get_project: 프로젝트 정보 조회
echo - get_issue: 단건 이슈 조회  
echo - search_issues: JQL 자유 검색
echo - get_project_versions: 프로젝트 버전 목록
echo - search_qa_issues: QA 관련 미리 정의된 검색

echo.
pause
