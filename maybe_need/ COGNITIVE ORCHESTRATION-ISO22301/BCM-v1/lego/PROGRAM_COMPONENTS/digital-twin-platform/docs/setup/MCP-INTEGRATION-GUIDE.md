# MCP Integration Guide for Digital Twin Module

## Overview
The Digital Twin Module now includes full MCP (Model Context Protocol) integration, allowing AI agents like Claude to directly interact with the system through standardized tools and resources.

## Features

### Available Tools
1. **create_digital_twin** - Create organization digital twins
2. **run_simulation** - Run various simulation scenarios
3. **analyze_organization** - AI-powered organization analysis
4. **predict_trends** - Predict future trends using AI
5. **optimize_parameters** - Optimize organization parameters
6. **get_metrics** - Retrieve performance metrics
7. **list_twins** - List available digital twins
8. **generate_report** - Generate comprehensive reports

### Simulation Scenarios
- Budget optimization
- Crisis management
- Scaling analysis
- Efficiency improvement
- Grant impact assessment
- Staff reorganization

### AI Capabilities
- Multi-model support (OpenAI, Anthropic, local)
- Predictive analytics
- Pattern recognition
- Natural language processing
- Self-learning and adaptation

## Installation

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `.env` file with your settings:
```env
# Database (choose one)
DATABASE_TYPE=memory  # or postgresql, mongodb, redis

# AI Configuration (optional)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here

# Security
JWT_SECRET=generate-strong-secret-here
ENCRYPTION_KEY=base64-encoded-32-byte-key
```

### 3. Start MCP Server
```bash
npm run mcp:start
```

## Claude Desktop Integration

### Method 1: Direct Configuration
Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "digital-twin": {
      "command": "node",
      "args": [
        "/path/to/digital-twin-standalone/mcp-server/digital-twin-mcp-server.js"
      ],
      "env": {
        "NODE_ENV": "production",
        "DATABASE_TYPE": "memory"
      }
    }
  }
}
```

### Method 2: Using NPX
```json
{
  "mcpServers": {
    "digital-twin": {
      "command": "npx",
      "args": [
        "-y",
        "digital-twin-mcp-server"
      ]
    }
  }
}
```

## Usage Examples

### Create Organization
```
Use the create_digital_twin tool to create a new NPO:
- Organization ID: npo-001
- Name: Green Future Foundation
- Type: charity
- Mission: Environmental conservation
- Size: 50 employees
- Annual budget: $2,000,000
```

### Run Simulation
```
Run a budget optimization simulation for npo-001:
- Scenario: budget_optimization
- Time horizon: 365 days
- Objective: maximize impact
```

### Generate Report
```
Generate an executive summary report for npo-001:
- Report type: executive_summary
- Format: markdown
```

## API Reference

### Tool: create_digital_twin
**Input:**
- `organizationId` (string, required): Unique identifier
- `name` (string, required): Organization name
- `type` (string, required): Organization type
- `mission` (string): Mission statement
- `size` (number): Number of employees
- `annualBudget` (number): Annual budget
- `departments` (array): Department structure

**Output:**
- Digital twin ID
- Initial state
- Health metrics

### Tool: run_simulation
**Input:**
- `twinId` (string, required): Digital twin ID
- `scenario` (string, required): Scenario type
- `parameters` (object): Scenario parameters
- `timeHorizon` (number): Days to simulate

**Output:**
- Simulation results
- Predictions
- Recommendations

### Tool: analyze_organization
**Input:**
- `twinId` (string, required): Digital twin ID
- `analysisType` (string, required): Type of analysis
- `depth` (string): Analysis depth (quick/standard/comprehensive)

**Output:**
- Analysis results
- Findings
- Insights
- Recommendations

## Resources

The MCP server provides access to these resources:
- `twin://documentation` - Complete system documentation
- `twin://templates/organization` - Organization templates
- `twin://scenarios` - Scenario definitions
- `twin://metrics/definitions` - Metric definitions

## Security

All MCP requests are:
- Validated for input security
- Rate limited
- Audit logged
- Encrypted in transit
- Authenticated (when configured)

## Troubleshooting

### Server Won't Start
1. Check Node.js version (>=18.0.0)
2. Verify all dependencies installed
3. Check environment variables
4. Review logs in console

### Connection Issues
1. Verify server is running
2. Check Claude Desktop config path
3. Ensure proper permissions
4. Test with simple tool first

### Database Errors
1. Check DATABASE_TYPE setting
2. Verify database credentials
3. Test connection separately
4. Use 'memory' type for testing

## Development

### Testing MCP Server
```bash
# Run in development mode
npm run mcp:dev

# Test with MCP Inspector
npx @modelcontextprotocol/inspector
```

### Adding New Tools
1. Define tool in `setupHandlers()`
2. Create handler method
3. Add input schema validation
4. Update documentation

### Debugging
Enable debug logging:
```bash
DEBUG=* npm run mcp:start
```

## Performance Optimization

### Caching
- AI responses cached for 1 hour
- Database queries cached for 5 minutes
- Simulation results cached indefinitely

### Rate Limiting
- 100 requests per 15 minutes per client
- Configurable via RATE_LIMIT_REQUESTS

### Database Optimization
- Indexed queries for fast lookup
- Connection pooling enabled
- Automatic query optimization

## Production Deployment

### Prerequisites
- PostgreSQL or MongoDB for production
- Redis for caching (recommended)
- SSL certificates for HTTPS
- API keys for AI providers

### Deployment Steps
1. Set NODE_ENV=production
2. Configure production database
3. Set up monitoring
4. Enable security features
5. Configure backups

### Monitoring
Monitor these metrics:
- Request rate
- Response time
- Error rate
- Database performance
- AI API usage

## Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Test with MCP Inspector
4. Create GitHub issue

## License

MIT License - See LICENSE file for details