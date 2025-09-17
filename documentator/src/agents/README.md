# Digital Office Agents

This directory contains all autonomous agents for the Digital Office platform.

## Directory Structure

```
agents/
├── monitoring/     # Agents for system and project monitoring
├── automation/     # Agents for automated tasks and workflows
├── integration/    # Agents for external system integration
├── analytics/      # Agents for data analysis and reporting
└── custom/         # Custom user-defined agents
```

## Creating a New Agent

Each agent must have the following structure:

```
agent-name/
├── agent.json      # Agent manifest file
├── index.ts        # Agent implementation
└── README.md       # Agent documentation (optional)
```

### Agent Manifest (agent.json)

```json
{
  "name": "example-agent",
  "version": "1.0.0",
  "description": "Example agent description",
  "category": "automation",
  "entryPoint": "index.js",
  "className": "ExampleAgent",
  "dependencies": [],
  "config": {
    "customParam": "value"
  },
  "autoStart": false,
  "enabled": true
}
```

### Agent Implementation (index.ts)

```typescript
import { BaseAgent } from '../../core/BaseAgent';
import { ScheduleConfig, ScheduleType, AgentConfig } from '../../types/AgentInterface';

export class ExampleAgent extends BaseAgent {
  constructor(config: AgentConfig) {
    super(config);

    this.metadata = {
      name: 'example-agent',
      version: '1.0.0',
      description: 'Example autonomous agent',
      category: 'automation'
    };
  }

  getScheduleConfig(): ScheduleConfig {
    return {
      type: ScheduleType.INTERVAL,
      enabled: true,
      intervalMs: 60000, // Run every minute
      stopOnError: false
    };
  }

  async executeAutonomously(): Promise<void> {
    // Agent logic here
    this.log('Executing agent task...');

    // Use built-in methods
    await this.emit('agent.task.completed', { success: true });
    await this.saveData('lastRun', Date.now());
  }

  // Optional lifecycle hooks
  protected async onInitialize(): Promise<void> {
    this.log('Agent initializing...');
  }

  protected async onShutdown(): Promise<void> {
    this.log('Agent shutting down...');
  }

  // MCP tool handlers (if needed)
  getTools() {
    return [];
  }

  async handleToolCall(toolName: string, args: any) {
    throw new Error('No tools available');
  }
}
```

## Available Infrastructure

All agents have access to:

### 1. **EventBus** - For communication
```typescript
// Emit events
await this.emit('custom.event', { data });

// Subscribe to events
await this.on('some.event', async (data) => {
  // Handle event
});
```

### 2. **DataStore** - For data persistence
```typescript
// Save data
await this.saveData('key', value);

// Load data
const value = await this.loadData('key');

// Query data
const results = await this.queryData({ status: 'active' });
```

### 3. **ResourceManager** - For resource access
```typescript
// File operations
const content = await this.readFile('/path/to/file');
await this.writeFile('/path/to/file', content);

// System resources
const resources = await this.getSystemResources();

// Execute commands
const { stdout } = await this.executeCommand('ls -la');

// API calls
const data = await this.fetchApi('github', '/repos/user/repo');
```

### 4. **Service Access**
```typescript
// Get service instance
const documentator = this.getService('documentator');
```

## Schedule Types

Agents can use different scheduling strategies:

- **INTERVAL** - Run at fixed intervals
- **CRON** - Run on cron schedule
- **ONCE** - Run once after delay
- **EVENT_DRIVEN** - Run on specific events

## Agent Lifecycle

1. **Load** - Agent manifest loaded from disk
2. **Instantiate** - Agent class created
3. **Initialize** - Agent initialized, resources allocated
4. **Register** - Agent registered with scheduler
5. **Execute** - Agent runs according to schedule
6. **Shutdown** - Agent stopped and resources freed

## Best Practices

1. Always handle errors gracefully
2. Use logging for debugging
3. Clean up resources in onShutdown
4. Set appropriate resource quotas
5. Emit events for important actions
6. Store state in DataStore for persistence
7. Use appropriate schedule intervals
8. Document your agent thoroughly

## Examples

See the example agents in each category folder for implementation patterns.