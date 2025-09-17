const fs = require('fs-extra');
const path = require('path');

/**
 * Post-build script for Digital Office Hub installer
 * Runs after Electron Builder completes the build
 */

async function postBuild() {
  console.log('🔧 Running post-build script...');

  try {
    // Create release info file
    const packageJson = await fs.readJson('../package.json');
    const releaseInfo = {
      name: 'Digital Office Hub',
      version: packageJson.version,
      buildDate: new Date().toISOString(),
      platform: process.platform,
      arch: process.arch,
      installer: {
        features: [
          'Automated system requirements check',
          'Node.js auto-installation',
          'Claude Desktop integration',
          'Desktop and Start Menu shortcuts',
          'Automatic dependency installation'
        ],
        requirements: {
          os: 'Windows 10 or later',
          memory: '2GB RAM (minimum)',
          storage: '1GB free space',
          nodejs: '18.0.0 or later (auto-installed if missing)'
        }
      }
    };

    // Write release info
    await fs.writeJson('dist/release-info.json', releaseInfo, { spaces: 2 });
    console.log('✅ Created release info file');

    // Check if installer was created successfully
    const installerFiles = await fs.readdir('dist').catch(() => []);
    const exeFiles = installerFiles.filter(file => file.endsWith('.exe'));

    if (exeFiles.length > 0) {
      console.log('✅ Installer created successfully:');
      for (const file of exeFiles) {
        const filePath = path.join('dist', file);
        const stats = await fs.stat(filePath);
        const sizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
        console.log(`   📦 ${file} (${sizeInMB} MB)`);
      }
    } else {
      console.log('⚠️ No exe files found in dist folder');
    }

    // Create installation instructions
    const instructions = `# Digital Office Hub Installer

## Installation Instructions

1. **Download the installer**: \`Digital Office Hub Setup.exe\`
2. **Run as administrator**: Right-click and select "Run as administrator" (recommended)
3. **Follow the setup wizard**:
   - Welcome screen with feature overview
   - System requirements check (automatic)
   - Configuration options
   - Installation progress
   - Completion and next steps

## System Requirements

- **Operating System**: Windows 10 or later
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 1GB free disk space
- **Network**: Internet connection for dependency installation

## Features Installed

- Digital Office Hub core platform
- MCP (Model Context Protocol) integration
- Agent management system
- REST API server
- Web interface (optional)
- Integration services for calendars and task management
- Claude Desktop auto-configuration

## Automatic Dependencies

The installer will automatically:
- Check system requirements
- Install Node.js if missing
- Install npm dependencies
- Compile TypeScript code
- Configure Claude Desktop (if installed)
- Create desktop and start menu shortcuts

## After Installation

1. **Restart Claude Desktop** (if configured)
2. **Verify MCP integration**: In Claude, type "List available MCP tools"
3. **Access web interface**: http://localhost:4000 (if enabled)
4. **View documentation**: Check the installed documentation folder

## Troubleshooting

- If installation fails, check the log file in the installer temp directory
- Ensure you have administrator privileges
- Verify internet connection for dependency downloads
- Check Windows Defender/antivirus settings if the installer is blocked

## Manual Configuration

If automatic Claude Desktop configuration fails:
1. Open Claude Desktop settings
2. Add MCP server configuration:
   \`\`\`json
   {
     "mcpServers": {
       "digital-office": {
         "command": "node",
         "args": ["C:\\\\Program Files\\\\Digital Office Hub\\\\dist\\\\index-new.js"],
         "env": {
           "NODE_ENV": "production"
         }
       }
     }
   }
   \`\`\`
3. Restart Claude Desktop

## Support

For issues or questions:
- Check the documentation in the installation folder
- Review log files in the logs directory
- Ensure all system requirements are met

Generated: ${new Date().toLocaleString()}
Version: ${packageJson.version}
`;

    await fs.writeFile('dist/INSTALLATION.md', instructions, 'utf8');
    console.log('✅ Created installation instructions');

    // Create a simple HTML page for release info
    const htmlPage = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Digital Office Hub v${releaseInfo.version || packageJson.version} - Release Info</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #2196f3; margin-bottom: 10px; }
        h2 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 5px; }
        .version { color: #666; font-size: 18px; margin-bottom: 30px; }
        .feature { background: #e3f2fd; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .req { background: #fff3e0; padding: 10px; margin: 5px 0; border-radius: 4px; }
        .build-info { color: #666; font-size: 14px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Digital Office Hub</h1>
        <div class="version">Version ${releaseInfo.version || packageJson.version}</div>

        <h2>Features</h2>
        ${releaseInfo.installer.features.map(f => `<div class="feature">• ${f}</div>`).join('')}

        <h2>System Requirements</h2>
        ${Object.entries(releaseInfo.installer.requirements).map(([key, value]) =>
          `<div class="req"><strong>${key.toUpperCase()}:</strong> ${value}</div>`
        ).join('')}

        <div class="build-info">
            Built on ${new Date(releaseInfo.buildDate).toLocaleString()}<br>
            Platform: ${releaseInfo.platform} (${releaseInfo.arch})
        </div>
    </div>
</body>
</html>`;

    await fs.writeFile('dist/release.html', htmlPage, 'utf8');
    console.log('✅ Created release info HTML page');

  } catch (error) {
    console.error('❌ Post-build script failed:', error);
    process.exit(1);
  }

  console.log('🎉 Post-build script completed successfully!');
}

// Run if called directly
if (require.main === module) {
  postBuild();
}

module.exports = postBuild;