# SSG Jira MCP Server

SSG.COM의 Jira 시스템에 접근할 수 있는 MCP(Model Context Protocol) 서버입니다.

## 🚀 설치 및 설정

### 1. 필요한 패키지 설치
```bash
cd C:\ssg\claude\mcp-jira-server
pip install -r requirements.txt
```

### 2. Claude Desktop 설정
Claude Desktop의 설정 파일에 다음 내용을 추가하세요:

**Windows 설정 파일 위치**: `%APPDATA%\Claude\claude_desktop_config.json`

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

### 3. Jira API 토큰 생성
1. SSG Jira (https://project.ssgadm.com)에 로그인
2. 우측 상단 프로필 → 계정 설정
3. 보안 → API 토큰 생성
4. 토큰 이름 입력 후 생성

## 📋 사용 가능한 도구

### 인증 설정
- **configure_auth**: Jira 계정과 API 토큰 설정

### 기본 조회
- **get_project**: 프로젝트 정보 조회
- **get_issue**: 단건 이슈 조회  
- **get_project_versions**: 프로젝트 버전 목록 조회

### 검색 기능
- **search_issues**: 자유로운 JQL 검색
- **search_qa_issues**: QA 관련 미리 정의된 검색
  - `in_progress_epics`: 진행중인 에픽들
  - `qa_target`: QA 대상 이슈들
  - `deploy_waiting`: 배포 대기중인 이슈들
  - `epic_issues`: 특정 에픽의 하위 이슈들

## 🔧 사용 방법

1. **Claude Desktop 재시작**
2. **인증 설정** (최초 1회):
   ```
   configure_auth 도구를 사용하여 Jira 계정과 API 토큰을 설정
   ```
3. **데이터 조회**:
   ```
   다른 도구들을 사용하여 필요한 Jira 데이터 조회
   ```

## 📝 예시 JQL 쿼리

```sql
-- 진행중인 에픽들
project in ("QAQ","이벤트 운영 QA") AND type = Epic AND status = "In Progress"

-- QA 대상 이슈들
project in ("QAQ","APP 운영 QA") AND "QA 대상" = Y

-- 특정 픽스 버전의 배포 대기 이슈들
"배포 진행" = YES AND fixVersion = "25년 1월 15일 정기 - SERVER"

-- 특정 에픽의 하위 이슈들
"Epic Link" = QAQ-777
```

## 🛠️ 지원하는 커스텀 필드

- `customfield_10521`: QA/테스트 담당자
- `customfield_10706`: 배포일자  
- `customfield_10209`: 시작일
- `customfield_10210`: 종료일
- `customfield_12213`: QA 대상
- `customfield_10103`: 에픽명

## 🔍 테스트

서버가 정상적으로 작동하는지 테스트:
```bash
cd C:\ssg\claude\mcp-jira-server
python ssg_jira_mcp_server.py
```

## 📞 문의

이슈나 개선사항이 있으시면 SSG D/I본부 관련 팀에 문의하세요.
