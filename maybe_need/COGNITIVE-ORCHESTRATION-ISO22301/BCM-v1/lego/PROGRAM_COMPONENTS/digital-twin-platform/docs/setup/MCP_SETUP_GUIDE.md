# MCP Integration Setup Guide

## For Claude Desktop Users

### 1. Add to Claude Desktop Config

Add this to your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "digital-twin": {
      "command": "node",
      "args": ["/Users/maksymdemchenko/claude_workspace_files/Development/digital-twin-standalone/mcp-server/digital-twin-mcp-server.js"],
      "env": {
        "NODE_ENV": "production",
        "SUPABASE_URL": "YOUR_SUPABASE_URL",
        "SUPABASE_ANON_KEY": "YOUR_SUPABASE_ANON_KEY"
      }
    }
  }
}
```

### 2. Restart Claude Desktop

After adding the configuration, restart Claude Desktop.

### 3. Available Tools

Once connected, you'll have access to these tools:

- `create_digital_twin` - Create a new digital twin for an organization
- `run_simulation` - Run various simulation scenarios
- `analyze_organization` - AI-powered organization analysis
- `predict_trends` - Predict future trends using AI
- `optimize_parameters` - Optimize organization parameters
- `get_metrics` - Get current metrics for a digital twin
- `list_twins` - List all available digital twins
- `generate_report` - Generate comprehensive reports

## For Web Claude Users

The MCP server can also be accessed through the web interface:

1. Navigate to: http://localhost:3000
2. Click on "AI Assistant" tab
3. The MCP tools will be available through the interface

## For Claude Code Users

Claude Code can use the MCP server directly through the configured tools.

## Testing the Connection

To test if MCP is working, ask Claude:
"Can you list the available digital twins using the MCP tools?"

Claude should be able to use the `list_twins` tool to query the system.

## Available Resources

The MCP server provides these resources:
- `twin://documentation` - Complete documentation
- `twin://templates/organization` - Organization templates
- `twin://scenarios` - Simulation scenarios
- `twin://metrics/definitions` - Metrics definitions

## Security Notes

- All requests are validated through the Security Manager
- Authentication is required for sensitive operations
- Audit logging is enabled for all tool usage
- Rate limiting is applied to prevent abuse

## Troubleshooting

### MCP Server Not Connecting
1. Check that Node.js is installed: `node --version`
2. Verify the path to the MCP server file is correct
3. Check environment variables are set correctly

### Tools Not Available
1. Restart Claude Desktop after configuration changes
2. Check the MCP server logs: `tail -f ~/.claude/logs/mcp.log`
3. Verify the server starts without errors: `node mcp-server/digital-twin-mcp-server.js`

### Permission Errors
1. Ensure the MCP server file has execute permissions
2. Check Supabase credentials are valid
3. Verify database connection is working

## Support

For issues or questions:
- Check logs in: `~/.claude/logs/`
- Server logs: `./logs/mcp-server.log`
- Contact: support@digitaltwin.ai