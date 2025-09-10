# MCP Setup Instructions for Documentator

Follow these steps to add Documentator as a custom MCP connector in Claude Desktop.

## Prerequisites

- Node.js 18+ installed
- Claude Desktop application

## Installation Steps

### 1. Install Documentator

Open terminal/command prompt and run:

```bash
npm install -g @anthropic/documentator
```

### 2. Initialize Setup

Run the setup command to create the projects directory and example templates:

```bash
documentator-setup
```

This will:
- Create `~/projects/` directory (or `%USERPROFILE%\projects\` on Windows)
- Add an example project with a sample template
- Display the configuration you need for Claude Desktop

### 3. Locate Claude Desktop Configuration

Find your Claude Desktop configuration file:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/claude/claude_desktop_config.json
```

### 4. Add Documentator to Configuration

Open the `claude_desktop_config.json` file and add the Documentator MCP server:

**If the file is empty or doesn't exist, create it with:**
```json
{
  "mcpServers": {
    "documentator": {
      "command": "documentator"
    }
  }
}
```

**If you already have other MCP servers, add documentator to the existing structure:**
```json
{
  "mcpServers": {
    "your-existing-server": {
      "command": "some-other-command"
    },
    "documentator": {
      "command": "documentator"
    }
  }
}
```

### 5. Restart Claude Desktop

Close and reopen Claude Desktop completely to load the new configuration.

## Verify Installation

### Test Basic Functionality

In Claude Desktop, try these commands:

1. **List projects:**
   ```
   Show me all my projects
   ```

2. **Analyze the example project:**
   ```
   Analyze project "example-reports"
   ```

3. **Generate a test report:**
   ```
   Create a report from project "example-reports" using template "simple-report" with:
   - title: "My Test Report"
   - author: "Your Name"
   - content: "This is a test of the Documentator system"
   ```

### Expected Results

- **List projects:** Should show "example-reports" project
- **Analyze project:** Should show template details and variables
- **Generate report:** Should create a markdown file in your projects directory

## Creating Your Own Projects

### 1. Create Project Directory

Create a new folder in your projects directory:

```bash
# Windows
mkdir "%USERPROFILE%\projects\my-project"

# macOS/Linux  
mkdir ~/projects/my-project
```

### 2. Add Template Files

Create `.md` files with your templates. Example `weekly-report.md`:

```markdown
# Weekly Report - {{week}}

**Team:** {{team}}
**Period:** {{startDate}} to {{endDate}}

## Accomplishments

{{#if accomplishments}}
{{#each accomplishments as item}}
-  {{item}}
{{/each}}
{{#else}}
No major accomplishments this week.
{{/if}}

## Upcoming Tasks

{{#if upcomingTasks}}
{{#each upcomingTasks as task}}
-  {{task}}
{{/each}}
{{#else}}
Tasks for next week to be determined.
{{/if}}

## Notes

{{notes|No additional notes.}}
```

### 3. Use in Claude

```
Create a report from project "my-project" using template "weekly-report" with:
- week: "Week of January 15-21, 2024"
- team: "Development Team"
- startDate: "January 15"
- endDate: "January 21"
- accomplishments: ["Completed API integration", "Fixed critical bugs", "Updated documentation"]
- upcomingTasks: ["Start new feature", "Code review", "Team meeting"]
- notes: "Great progress this week!"
```

## Template Syntax Reference

| Syntax | Description | Example |
|--------|-------------|---------|
| `{{variable}}` | Simple variable replacement | `{{title}}` |
| `{{variable\|default}}` | Variable with fallback value | `{{author\|Unknown}}` |
| `{{#if condition}}...{{/if}}` | Conditional content | `{{#if hasData}}Show this{{/if}}` |
| `{{#each array as item}}...{{/each}}` | Loop through array | `{{#each tasks as task}}{{task}}{{/each}}` |

## Troubleshooting

### Common Issues

**"documentator command not found"**
- Ensure Node.js is installed
- Try reinstalling: `npm uninstall -g @anthropic/documentator && npm install -g @anthropic/documentator`
- Check PATH environment variable includes npm global directory

**"No projects found"**
- Run `documentator-setup` again
- Manually check if projects directory exists
- Verify directory permissions

**Claude doesn't recognize MCP commands**
- Restart Claude Desktop completely
- Verify configuration file syntax (use a JSON validator)
- Check Claude Desktop logs for errors

**Templates not found**
- Ensure template files have `.md` extension
- Check file names match what you're referencing in Claude
- Verify files are in the correct project subdirectory

### Advanced Configuration

**Custom projects directory:**
You can set a custom directory by modifying the MCP server configuration:

```json
{
  "mcpServers": {
    "documentator": {
      "command": "documentator",
      "env": {
        "DOCUMENTATOR_PROJECTS_DIR": "/path/to/your/custom/projects"
      }
    }
  }
}
```

**Debug mode:**
Enable debug logging:

```json
{
  "mcpServers": {
    "documentator": {
      "command": "documentator",
      "env": {
        "DEBUG": "true"
      }
    }
  }
}
```

## Support

- **Issues:** Report at https://github.com/anthropics/documentator/issues
- **Documentation:** Full docs at https://github.com/anthropics/documentator
- **Community:** Join discussions in Claude Desktop community forums

## Next Steps

1. Create your first custom project
2. Experiment with template syntax
3. Build templates for your common reporting needs
4. Share templates with your team

Happy documenting! 