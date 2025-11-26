# SSG Jira MCP Server - 환경 변수 인증 방식

## 🚀 설정 방법

### 1. 패키지 설치
```bash
cd C:\ssg\claude\mcp-jira-server
pip install -r requirements.txt
```

### 2. Jira API 토큰 생성
1. SSG Jira 접속: https://project.ssgadm.com
2. 프로필 → 계정 설정 → 보안 → API 토큰 생성
3. 토큰 이름: "Claude MCP Server"
4. 생성된 토큰 복사

### 3. Claude Desktop 설정
**파일 위치**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ssg-jira": {
      "command": "python",
      "args": [
        "C:\\ssg\\claude\\mcp-jira-server\\ssg_jira_mcp_server.py"
      ],
      "env": {
        "JIRA_USERNAME": "your-email@ssg.com",
        "JIRA_API_TOKEN": "ATATT3xFfGF0T4JaL2QVQjnOLlvuGOPS8NK..."
      }
    }
  }
}
```

**중요**: `your-email@ssg.com`과 `ATATT3xFfGF0T4JaL2QVQjnO...`를 실제 값으로 변경하세요.

### 4. Claude Desktop 재시작
설정 파일 수정 후 Claude Desktop을 재시작하세요.

## 🔧 대안 설정 방법

### 방법 1: 명령행 인수 사용
```json
{
  "mcpServers": {
    "ssg-jira": {
      "command": "python",
      "args": [
        "C:\\ssg\\claude\\mcp-jira-server\\ssg_jira_mcp_server.py",
        "--username", "your-email@ssg.com",
        "--api_token", "your-api-token"
      ]
    }
  }
}
```

### 방법 2: 시스템 환경 변수 사용
1. Windows 시스템 환경 변수 설정:
   - `JIRA_USERNAME=your-email@ssg.com`
   - `JIRA_API_TOKEN=your-api-token`

2. Claude Desktop 설정:
```json
{
  "mcpServers": {
    "ssg-jira": {
      "command": "python",
      "args": [
        "C:\\ssg\\claude\\mcp-jira-server\\ssg_jira_mcp_server.py"
      ]
    }
  }
}
```

## 🔍 사용 가능한 도구

인증이 자동으로 설정되면 다음 도구들을 바로 사용할 수 있습니다:

1. **get_project** - 프로젝트 정보 조회
2. **get_issue** - 단건 이슈 조회
3. **search_issues** - JQL 자유 검색
4. **get_project_versions** - 프로젝트 버전 목록
5. **search_qa_issues** - QA 관련 미리 정의된 검색

## 📝 사용 예시

Claude Desktop에서 다음과 같이 요청하세요:

```
get_project 도구를 사용해서 QAQ 프로젝트 정보를 조회해줘.
```

```
search_qa_issues 도구를 사용해서 진행중인 에픽들을 찾아줘.
- search_type: in_progress_epics
```

```
search_issues 도구를 사용해서 다음 JQL로 검색해줘:
project = QAQ AND status = "In Progress" AND assignee = currentUser()
```

## 🛠️ 문제 해결

### 인증 오류가 발생하는 경우:
1. API 토큰이 올바른지 확인
2. 사용자명(이메일)이 정확한지 확인
3. Jira 프로젝트 접근 권한 확인

### MCP 서버가 연결되지 않는 경우:
1. Python 경로가 올바른지 확인
2. 필요한 패키지가 설치되었는지 확인 (`pip install -r requirements.txt`)
3. Claude Desktop 완전 재시작

### 로그 확인:
Claude Desktop에서 도구 사용 시 오류가 발생하면 자세한 오류 메시지가 표시됩니다.

## 🔒 보안 주의사항

- API 토큰은 민감한 정보입니다. 안전하게 관리하세요.
- 설정 파일을 공유하지 마세요.
- 주기적으로 API 토큰을 갱신하는 것을 권장합니다.

## 📞 지원

문제가 발생하면 SSG D/I본부 관련 팀에 문의하세요.
