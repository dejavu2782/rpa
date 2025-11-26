@echo off
echo Installing MCP Server for Confluence...

cd /d "C:\ssg\claude\mcp-confluence-server"

echo Installing dependencies...
npm install

echo.
echo Setup completed!
echo.
echo Next steps:
echo 1. Copy claude_desktop_config.json to your Claude Desktop config folder
echo    Usually: %%APPDATA%%\Claude\claude_desktop_config.json
echo 2. Edit the config file and fill in your Confluence credentials
echo 3. Restart Claude Desktop
echo.
echo For Confluence API token:
echo 1. Go to https://projectwiki.ssgadm.com
echo 2. User Settings > Personal Access Tokens
echo 3. Create new token with read permissions
echo.
pause
