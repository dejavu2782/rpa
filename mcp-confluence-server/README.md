# Confluence MCP Server

Confluence 사이트에 접근하기 위한 MCP(Model Context Protocol) 서버입니다.

## 기능

- **search_confluence**: Confluence 내용 검색
- **get_page**: 특정 페이지 조회
- **list_spaces**: 사용 가능한 스페이스 목록
- **get_space_content**: 특정 스페이스의 콘텐츠 조회

## 설치 방법

1. `install.bat` 실행하여 의존성 설치
2. `claude_desktop_config.json`을 Claude Desktop 설정 폴더로 복사
3. 설정 파일에서 인증 정보 입력

## 인증 설정

Claude Desktop 설정 파일의 `env` 섹션에 인증 정보를 입력합니다:

### 방법 1: Username + API Token
```json
"env": {
  "CONFLUENCE_USERNAME": "your_username",
  "CONFLUENCE_TOKEN": "your_api_token"
}
```

### 방법 2: Bearer Token만 사용
```json
"env": {
  "CONFLUENCE_TOKEN": "your_bearer_token"
}
```

## Claude Desktop 설정

`%APPDATA%\Claude\claude_desktop_config.json` 파일을 다음과 같이 업데이트:

```json
{
  "mcpServers": {
    "confluence": {
      "command": "node",
      "args": ["C:\\ssg\\claude\\mcp-confluence-server\\server.js"],
      "env": {
        "CONFLUENCE_USERNAME": "your_username",
        "CONFLUENCE_TOKEN": "your_api_token"
      }
    }
  }
}
```

## 사용 방법

Claude Desktop을 재시작한 후, 다음과 같이 사용 가능:

- "프로젝트 관련 문서를 검색해줘"
- "특정 스페이스의 내용을 보여줘"
- "페이지 ID로 문서 내용을 가져와줘"

## 문제 해결

1. **인증 오류**: Confluence 로그인 정보와 API 토큰 확인
2. **접속 오류**: 네트워크 연결 및 URL 확인
3. **권한 오류**: Confluence에서 해당 스페이스 접근 권한 확인
