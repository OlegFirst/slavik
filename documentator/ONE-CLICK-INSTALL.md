# One-Click Installation for Documentator

Get Documentator working with Claude Desktop in just one step!

## 🚀 Quick Start

### Windows
1. Download the installer files
2. Double-click `install.bat`
3. Done! 🎉

### macOS/Linux
1. Download the installer files
2. Open Terminal in the download folder
3. Run: `bash install.sh`
4. Done! 🎉

## What the installer does automatically:

✅ **Checks Node.js** - Ensures you have Node.js installed  
✅ **Installs Documentator** - Downloads and installs via npm  
✅ **Creates Projects Directory** - Sets up `~/projects/` with example  
✅ **Configures Claude Desktop** - Automatically adds MCP configuration  
✅ **Restarts Claude Desktop** - Applies changes immediately  

## After Installation

Open Claude Desktop and try:
```
Show me all my projects
```

You should see your example project! Then try:
```
Create a report from project "example-reports" using template "simple-report" with:
- title: "My First Auto-Generated Report"
- author: "Your Name"
- content: "This was created by the one-click installer!"
```

## What You Get

### 📁 Projects Directory
Located at:
- **Windows:** `%USERPROFILE%\projects\`
- **macOS/Linux:** `~/projects/`

### 📄 Example Project
- **Project:** `example-reports/`
- **Template:** `simple-report.md`
- **Variables:** title, author, content, conclusions

### ⚙️ Claude Desktop Config
Automatically added to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "documentator": {
      "command": "documentator"
    }
  }
}
```

## Create Your Own Projects

After installation, creating new projects is easy:

1. **Create a folder:** `~/projects/my-new-project/`
2. **Add a template:** `my-template.md`
3. **Use in Claude:** "Analyze project my-new-project"

## Troubleshooting

### "Node.js not found"
- Install Node.js from https://nodejs.org/
- Restart your terminal/command prompt
- Run the installer again

### "Permission denied" (macOS/Linux)
```bash
chmod +x install.sh
./install.sh
```

### "Claude Desktop not found"
- Install Claude Desktop first: https://claude.ai/download
- The installer will configure it, but it needs to be installed first

### Manual Fallback
If automatic installation fails, you can still install manually:
```bash
npm install -g @anthropic/documentator
documentator-setup
# Then add to Claude Desktop config manually
```

## Files in This Package

- **`install.bat`** - Windows installer
- **`install.sh`** - macOS/Linux installer  
- **`one-click-install.js`** - Core installer logic
- **`ONE-CLICK-INSTALL.md`** - This instruction file

## Why One-Click?

Instead of asking users to:
1. Install npm package ✅ *Done automatically*
2. Run setup command ✅ *Done automatically*  
3. Find Claude config file ✅ *Done automatically*
4. Edit JSON configuration ✅ *Done automatically*
5. Restart Claude Desktop ✅ *Done automatically*

You just run **one** file and everything works! 🎯

## Requirements

- **Node.js 18+** (installer will check and guide you)
- **Claude Desktop** (must be installed first)
- **Internet connection** (to download packages)

## What Makes This Special

🔍 **Auto-detection** - Finds your system type and Claude config  
🛠️ **Auto-configuration** - Modifies Claude Desktop settings safely  
🔄 **Auto-restart** - Restarts Claude to apply changes  
📁 **Auto-setup** - Creates example project ready to use  
❌ **Error handling** - Graceful fallbacks if anything goes wrong  

Perfect for sharing with non-technical users! 🎉