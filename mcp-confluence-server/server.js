const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');
const axios = require('axios');

class ConfluenceServer {
  constructor() {
    this.server = new Server(
      {
        name: 'confluence-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.baseUrl = 'https://projectwiki.ssgadm.com';
    this.auth = null; // 인증 정보는 환경변수에서 로드
    
    this.setupToolHandlers();
    
    // 에러 핸들러 설정
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'search_confluence',
            description: 'Search for content in Confluence',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query'
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of results',
                  default: 10
                }
              },
              required: ['query']
            }
          },
          {
            name: 'get_page',
            description: 'Get a specific Confluence page by ID',
            inputSchema: {
              type: 'object',
              properties: {
                pageId: {
                  type: 'string',
                  description: 'Confluence page ID'
                }
              },
              required: ['pageId']
            }
          },
          {
            name: 'list_spaces',
            description: 'List all available Confluence spaces',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          },
          {
            name: 'get_space_content',
            description: 'Get content from a specific space',
            inputSchema: {
              type: 'object',
              properties: {
                spaceKey: {
                  type: 'string',
                  description: 'Confluence space key'
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of results',
                  default: 20
                }
              },
              required: ['spaceKey']
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'search_confluence':
            return await this.searchConfluence(args.query, args.limit || 10);
          case 'get_page':
            return await this.getPage(args.pageId);
          case 'list_spaces':
            return await this.listSpaces();
          case 'get_space_content':
            return await this.getSpaceContent(args.spaceKey, args.limit || 20);
          default:
            throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
        }
      } catch (error) {
        throw new McpError(ErrorCode.InternalError, `Tool execution failed: ${error.message}`);
      }
    });
  }

  async makeRequest(endpoint, params = {}) {
    try {
      const config = {
        method: 'GET',
        url: `${this.baseUrl}/rest/api${endpoint}`,
        params,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      };

      // 인증 정보가 있으면 추가 (Claude Desktop config에서 환경변수로 전달됨)
      if (process.env.CONFLUENCE_USERNAME && process.env.CONFLUENCE_TOKEN) {
        config.auth = {
          username: process.env.CONFLUENCE_USERNAME,
          password: process.env.CONFLUENCE_TOKEN
        };
      } else if (process.env.CONFLUENCE_TOKEN) {
        config.headers['Authorization'] = `Bearer ${process.env.CONFLUENCE_TOKEN}`;
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      console.error('Request failed:', error.response?.data || error.message);
      throw new Error(`API request failed: ${error.response?.status} ${error.response?.statusText}`);
    }
  }

  async searchConfluence(query, limit) {
    const data = await this.makeRequest('/content/search', {
      cql: `text ~ "${query}"`,
      limit,
      expand: 'body.view,space,version'
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            results: data.results?.map(item => ({
              id: item.id,
              title: item.title,
              type: item.type,
              space: item.space?.name,
              url: `${this.baseUrl}${item._links?.webui}`,
              excerpt: item.excerpt || '',
              lastModified: item.version?.when
            })) || [],
            total: data.size || 0
          }, null, 2)
        }
      ]
    };
  }

  async getPage(pageId) {
    const data = await this.makeRequest(`/content/${pageId}`, {
      expand: 'body.storage,space,version,ancestors'
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            id: data.id,
            title: data.title,
            type: data.type,
            space: data.space?.name,
            content: data.body?.storage?.value || '',
            url: `${this.baseUrl}${data._links?.webui}`,
            lastModified: data.version?.when,
            version: data.version?.number
          }, null, 2)
        }
      ]
    };
  }

  async listSpaces() {
    const data = await this.makeRequest('/space', {
      limit: 50,
      expand: 'description'
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            spaces: data.results?.map(space => ({
              key: space.key,
              name: space.name,
              type: space.type,
              description: space.description?.plain?.value || '',
              url: `${this.baseUrl}${space._links?.webui}`
            })) || [],
            total: data.size || 0
          }, null, 2)
        }
      ]
    };
  }

  async getSpaceContent(spaceKey, limit) {
    const data = await this.makeRequest('/content', {
      spaceKey,
      limit,
      expand: 'space,version'
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            content: data.results?.map(item => ({
              id: item.id,
              title: item.title,
              type: item.type,
              url: `${this.baseUrl}${item._links?.webui}`,
              lastModified: item.version?.when
            })) || [],
            total: data.size || 0
          }, null, 2)
        }
      ]
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Confluence MCP server running on stdio');
  }
}

const server = new ConfluenceServer();
server.run().catch(console.error);
