#!/usr/bin/env python3
"""
SSG Jira MCP Server
MCP 서버를 통해 SSG Jira 시스템에 접근할 수 있는 도구들을 제공합니다.
인증 정보는 환경 변수나 명령행 인수로 설정합니다.
"""

import asyncio
import json
import base64
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("ssg-jira-mcp")

class SSGJiraMCPServer:
    def __init__(self):
        self.server = Server("ssg-jira")
        self.base_url = "https://project.ssgadm.com"
        
        # 명령행 인수나 환경 변수에서 인증 정보 가져오기
        self.username: Optional[str] = self._get_auth_value("username")
        self.api_token: Optional[str] = self._get_auth_value("api_token")
        self.headers: Optional[Dict[str, str]] = None
        
        # 인증 정보가 있으면 자동으로 설정
        if self.username and self.api_token:
            self._setup_auth_headers()
            logger.info(f"✅ 인증 정보 자동 설정 완료: {self.username}")
        else:
            logger.warning("⚠️ 인증 정보가 설정되지 않았습니다. 환경 변수나 명령행 인수를 설정하세요.")
        
        # 도구 등록
        self.setup_tools()
    
    def _get_auth_value(self, key: str) -> Optional[str]:
        """명령행 인수 또는 환경 변수에서 인증 값을 가져옵니다."""
        # 1. 명령행 인수에서 확인
        arg_key = f"--{key}"
        if arg_key in sys.argv:
            idx = sys.argv.index(arg_key)
            if idx + 1 < len(sys.argv):
                return sys.argv[idx + 1]
        
        # 2. 환경 변수에서 확인
        env_key = f"JIRA_{key.upper()}"
        return os.getenv(env_key)
    
    def _setup_auth_headers(self):
        """인증 헤더를 설정합니다."""
        if self.username and self.api_token:
            credentials = f"{self.username}:{self.api_token}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            self.headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
    
    def setup_tools(self):
        """MCP 도구들을 설정합니다."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """사용 가능한 도구 목록을 반환합니다."""
            return [
                types.Tool(
                    name="get_project",
                    description="프로젝트 정보를 조회합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "프로젝트 키 (예: QAQ, WASD, PROMO)"
                            }
                        },
                        "required": ["project_key"]
                    }
                ),
                types.Tool(
                    name="search_issues",
                    description="JQL을 사용하여 이슈를 검색합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "jql": {
                                "type": "string",
                                "description": "JQL 쿼리 (예: project = QAQ AND status = 'In Progress')"
                            },
                            "fields": {
                                "type": "string",
                                "description": "조회할 필드 (콤마로 구분, 기본값: 주요 필드들)",
                                "default": "summary,status,priority,issuetype,assignee,created,updated"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "최대 결과 수 (기본값: 50)",
                                "default": 50
                            }
                        },
                        "required": ["jql"]
                    }
                ),
                types.Tool(
                    name="get_issue",
                    description="단건 이슈 정보를 조회합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "이슈 키 (예: QAQ-777, WASD-1251)"
                            },
                            "fields": {
                                "type": "string",
                                "description": "조회할 필드 (콤마로 구분, 기본값: 모든 필드)"
                            }
                        },
                        "required": ["issue_key"]
                    }
                ),
                types.Tool(
                    name="get_project_versions",
                    description="프로젝트의 버전 목록을 조회합니다",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "프로젝트 키 (예: QAQ, WASD)"
                            }
                        },
                        "required": ["project_key"]
                    }
                ),
                types.Tool(
                    name="search_qa_issues",
                    description="QA 관련 이슈를 검색합니다 (미리 정의된 JQL 사용)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_type": {
                                "type": "string",
                                "enum": ["in_progress_epics", "qa_target", "deploy_waiting", "epic_issues"],
                                "description": "검색 유형: in_progress_epics(진행중 에픽), qa_target(QA 대상), deploy_waiting(배포 대기), epic_issues(특정 에픽의 이슈들)"
                            },
                            "epic_key": {
                                "type": "string",
                                "description": "에픽 키 (search_type이 'epic_issues'일 때 필수)"
                            },
                            "fix_version": {
                                "type": "string",
                                "description": "픽스 버전 (search_type이 'deploy_waiting'일 때 선택사항)"
                            }
                        },
                        "required": ["search_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[types.TextContent]:
            """도구 호출을 처리합니다."""
            
            try:
                if name == "get_project":
                    return await self._get_project(arguments)
                elif name == "search_issues":
                    return await self._search_issues(arguments)
                elif name == "get_issue":
                    return await self._get_issue(arguments)
                elif name == "get_project_versions":
                    return await self._get_project_versions(arguments)
                elif name == "search_qa_issues":
                    return await self._search_qa_issues(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool execution error: {name}, {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=f"❌ 오류 발생: {str(e)}"
                )]
    
    async def _check_auth(self):
        """인증 정보가 설정되었는지 확인합니다."""
        if not self.headers:
            raise ValueError("인증 정보가 설정되지 않았습니다. 환경 변수 JIRA_USERNAME, JIRA_API_TOKEN을 설정하거나 명령행 인수 --username, --api_token을 사용하세요.")
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """HTTP 요청을 수행합니다."""
        await self._check_auth()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.request(
                    method, 
                    url, 
                    headers=self.headers,
                    params=params,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            raise
    
    async def _get_project(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """프로젝트 정보를 조회합니다."""
        project_key = arguments["project_key"]
        
        try:
            data = await self._make_request("GET", f"/rest/api/2/project/{project_key}")
            
            result = {
                "key": data.get("key"),
                "name": data.get("name"),
                "description": data.get("description"),
                "lead": data.get("lead", {}).get("displayName"),
                "projectTypeKey": data.get("projectTypeKey"),
                "category": data.get("projectCategory", {}).get("name") if data.get("projectCategory") else None
            }
            
            return [types.TextContent(
                type="text",
                text=f"📋 프로젝트 정보:\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
            )]
            
        except Exception as e:
            logger.error(f"Project fetch error: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"❌ 프로젝트 조회 실패: {str(e)}"
            )]
    
    async def _search_issues(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """JQL로 이슈를 검색합니다."""
        jql = arguments["jql"]
        fields = arguments.get("fields", "summary,status,priority,issuetype,assignee,created,updated")
        max_results = arguments.get("max_results", 50)
        
        try:
            params = {
                "jql": jql,
                "fields": fields,
                "maxResults": max_results
            }
            
            data = await self._make_request("GET", "/rest/api/2/search", params=params)
            
            issues = []
            for issue in data.get("issues", []):
                fields_data = issue.get("fields", {})
                issue_info = {
                    "key": issue.get("key"),
                    "summary": fields_data.get("summary"),
                    "status": fields_data.get("status", {}).get("name") if fields_data.get("status") else None,
                    "priority": fields_data.get("priority", {}).get("name") if fields_data.get("priority") else None,
                    "assignee": fields_data.get("assignee", {}).get("displayName") if fields_data.get("assignee") else None,
                    "created": fields_data.get("created"),
                    "updated": fields_data.get("updated")
                }
                issues.append(issue_info)
            
            result = {
                "total": data.get("total"),
                "maxResults": data.get("maxResults"),
                "startAt": data.get("startAt"),
                "issues": issues
            }
            
            return [types.TextContent(
                type="text",
                text=f"🔍 검색 결과 ({result['total']}건):\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```"
            )]
            
        except Exception as e:
            logger.error(f"Issue search error: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"❌ 이슈 검색 실패: {str(e)}"
            )]
    
    async def _get_issue(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """단건 이슈를 조회합니다."""
        issue_key = arguments["issue_key"]
        fields = arguments.get("fields")
        
        try:
            params = {"fields": fields} if fields else None
            data = await self._make_request("GET", f"/rest/api/2/issue/{issue_key}", params=params)
            
            fields_data = data.get("fields", {})
            
            # 주요 정보 추출
            issue_info = {
                "key": data.get("key"),
                "summary": fields_data.get("summary"),
                "description": fields_data.get("description"),
                "status": fields_data.get("status", {}).get("name") if fields_data.get("status") else None,
                "priority": fields_data.get("priority", {}).get("name") if fields_data.get("priority") else None,
                "issuetype": fields_data.get("issuetype", {}).get("name") if fields_data.get("issuetype") else None,
                "assignee": fields_data.get("assignee", {}).get("displayName") if fields_data.get("assignee") else None,
                "reporter": fields_data.get("reporter", {}).get("displayName") if fields_data.get("reporter") else None,
                "created": fields_data.get("created"),
                "updated": fields_data.get("updated"),
                "duedate": fields_data.get("duedate"),
                "project": fields_data.get("project", {}).get("name") if fields_data.get("project") else None,
                "labels": fields_data.get("labels", []),
                "fixVersions": [v.get("name") for v in fields_data.get("fixVersions", [])],
                # 커스텀 필드들
                "qa_담당자": fields_data.get("customfield_10521", {}).get("displayName") if fields_data.get("customfield_10521") else None,
                "배포일자": fields_data.get("customfield_10706"),
                "start_date": fields_data.get("customfield_10209"),
                "end_date": fields_data.get("customfield_10210"),
                "qa_대상": fields_data.get("customfield_12213", {}).get("value") if fields_data.get("customfield_12213") else None,
                "epic_name": fields_data.get("customfield_10103")
            }
            
            return [types.TextContent(
                type="text",
                text=f"📄 이슈 정보 ({issue_key}):\n```json\n{json.dumps(issue_info, indent=2, ensure_ascii=False)}\n```"
            )]
            
        except Exception as e:
            logger.error(f"Issue fetch error: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"❌ 이슈 조회 실패: {str(e)}"
            )]
    
    async def _get_project_versions(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """프로젝트 버전을 조회합니다."""
        project_key = arguments["project_key"]
        
        try:
            data = await self._make_request("GET", f"/rest/api/latest/project/{project_key}/versions")
            
            versions = []
            for version in data:
                version_info = {
                    "id": version.get("id"),
                    "name": version.get("name"),
                    "archived": version.get("archived"),
                    "released": version.get("released"),
                    "releaseDate": version.get("releaseDate"),
                    "description": version.get("description")
                }
                versions.append(version_info)
            
            return [types.TextContent(
                type="text",
                text=f"📦 프로젝트 버전 ({len(versions)}개):\n```json\n{json.dumps(versions, indent=2, ensure_ascii=False)}\n```"
            )]
            
        except Exception as e:
            logger.error(f"Version fetch error: {str(e)}")
            return [types.TextContent(
                type="text",
                text=f"❌ 버전 조회 실패: {str(e)}"
            )]
    
    async def _search_qa_issues(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """QA 관련 이슈를 검색합니다."""
        search_type = arguments["search_type"]
        
        # 미리 정의된 JQL 쿼리들
        jql_queries = {
            "in_progress_epics": 'project in ("QAQ","이벤트 운영 QA") AND type = Epic AND status = "In Progress"',
            "qa_target": 'project in ("QAQ","APP 운영 QA") AND "QA 대상" = Y',
            "deploy_waiting": '"배포 진행" = YES',
            "epic_issues": f'"Epic Link" = {arguments.get("epic_key", "")}'
        }
        
        if search_type == "deploy_waiting" and arguments.get("fix_version"):
            jql_queries["deploy_waiting"] += f' AND fixVersion = "{arguments["fix_version"]}"'
        
        jql = jql_queries.get(search_type)
        if not jql:
            return [types.TextContent(
                type="text",
                text=f"❌ 지원하지 않는 검색 유형: {search_type}"
            )]
        
        # 검색 실행
        search_args = {
            "jql": jql,
            "fields": "summary,status,priority,issuetype,assignee,created,updated,customfield_10521,customfield_12213",
            "max_results": 100
        }
        
        return await self._search_issues(search_args)
    
    async def run(self):
        """서버를 실행합니다."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ssg-jira",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    """메인 함수"""
    server = SSGJiraMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
