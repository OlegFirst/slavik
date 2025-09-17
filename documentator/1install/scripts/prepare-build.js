const fs = require('fs-extra');
const path = require('path');

/**
 * Pre-build script for Digital Office Hub installer
 * Prepares the build environment and copies necessary files
 */

async function prepareBuild() {
  console.log('📋 Preparing build environment...');

  try {
    // Ensure build directories exist
    await fs.ensureDir('temp-build');
    await fs.ensureDir('dist');
    await fs.ensureDir('assets');

    console.log('📁 Created build directories');

    // Copy main project files
    const mainProjectPath = path.resolve('..');
    const tempBuildPath = path.resolve('temp-build');

    // List of files/directories to copy from main project
    const filesToCopy = [
      { src: 'src', dest: 'src', type: 'dir' },
      { src: 'package.json', dest: 'package.json', type: 'file' },
      { src: 'tsconfig.json', dest: 'tsconfig.json', type: 'file' },
      { src: 'README.md', dest: 'README.md', type: 'file', optional: true }
    ];

    console.log('📋 Copying main project files...');
    for (const item of filesToCopy) {
      const srcPath = path.join(mainProjectPath, item.src);
      const destPath = path.join(tempBuildPath, item.dest);

      try {
        if (await fs.pathExists(srcPath)) {
          if (item.type === 'dir') {
            await fs.copy(srcPath, destPath, { overwrite: true });
            console.log(`   ✅ Copied directory: ${item.src}`);
          } else {
            await fs.copy(srcPath, destPath, { overwrite: true });
            console.log(`   ✅ Copied file: ${item.src}`);
          }
        } else if (!item.optional) {
          console.log(`   ⚠️ Missing required file: ${item.src}`);
        }
      } catch (error) {
        if (!item.optional) {
          throw error;
        }
        console.log(`   ⚠️ Optional file not copied: ${item.src}`);
      }
    }

    // Create installer-specific package.json for the temp build
    const mainPackageJson = await fs.readJson(path.join(mainProjectPath, 'package.json'));
    const installerPackageJson = {
      ...mainPackageJson,
      name: 'digital-office-hub-runtime',
      main: 'dist/index-new.js',
      scripts: {
        start: 'node dist/index-new.js',
        build: 'tsc'
      },
      // Only include runtime dependencies
      devDependencies: {}
    };

    await fs.writeJson(
      path.join(tempBuildPath, 'package.json'),
      installerPackageJson,
      { spaces: 2 }
    );
    console.log('   ✅ Created runtime package.json');

    // Create default .env file for production
    const envContent = `# Digital Office Hub - Production Configuration
NODE_ENV=production
JWT_SECRET=change-this-in-production-${Date.now()}
API_PORT=4000
MCP_PORT=3000
LOG_LEVEL=info
DATA_DIR=./data
ENABLE_WEB_INTERFACE=true
ENABLE_API_DOCS=true
CORS_ORIGINS=http://localhost:3000,http://localhost:4000
`;

    await fs.writeFile(path.join(tempBuildPath, '.env.example'), envContent);
    console.log('   ✅ Created .env.example');

    // Create assets if they don't exist
    const assetsPath = path.resolve('assets');

    // Create a simple icon if it doesn't exist
    if (!await fs.pathExists(path.join(assetsPath, 'icon.ico'))) {
      console.log('   ℹ️ Note: icon.ico not found - installer will use default');
      // Create a placeholder text file explaining how to add an icon
      const iconInstructions = `To add a custom icon to the installer:

1. Create or obtain an icon file in ICO format (icon.ico)
2. Place it in the assets/ directory
3. The icon should be at least 256x256 pixels
4. Rebuild the installer

The icon will be used for:
- Installer window
- Desktop shortcut
- Start Menu shortcut
- Windows Add/Remove Programs

Recommended icon specifications:
- Format: ICO
- Sizes: 16x16, 32x32, 48x48, 128x128, 256x256
- Color depth: 32-bit with transparency
`;
      await fs.writeFile(path.join(assetsPath, 'ICON_INSTRUCTIONS.txt'), iconInstructions);
    }

    // Create license file if it doesn't exist
    if (!await fs.pathExists(path.join(assetsPath, 'license.txt'))) {
      const licenseContent = `Digital Office Hub License Agreement

Copyright (c) ${new Date().getFullYear()} Digital Office Hub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This installer may download and install additional software components:
- Node.js (https://nodejs.org) - Subject to its own license terms
- npm packages - Subject to their respective license terms

By installing this software, you agree to the terms of this license and
acknowledge the third-party components and their licenses.
`;
      await fs.writeFile(path.join(assetsPath, 'license.txt'), licenseContent);
      console.log('   ✅ Created license.txt');
    }

    // Validate installer configuration
    console.log('🔍 Validating installer configuration...');

    const currentInstallerPackageJson = await fs.readJson('package.json');

    if (!currentInstallerPackageJson.build) {
      throw new Error('Missing Electron Builder configuration in package.json');
    }

    if (!currentInstallerPackageJson.build.nsis) {
      console.log('   ⚠️ NSIS configuration not found in package.json');
    }

    // Check for required files
    const requiredFiles = [
      'src/main.js',
      'src/installer.html',
      'src/installer.css',
      'src/installer.js'
    ];

    for (const file of requiredFiles) {
      if (!await fs.pathExists(file)) {
        throw new Error(`Required installer file missing: ${file}`);
      }
    }

    console.log('   ✅ All required files present');

    // Create build info file
    const buildInfo = {
      timestamp: new Date().toISOString(),
      version: currentInstallerPackageJson.version,
      nodeVersion: process.version,
      platform: process.platform,
      arch: process.arch,
      files: {
        copied: filesToCopy.length,
        tempBuildPath: tempBuildPath,
        assetsPath: assetsPath
      }
    };

    await fs.writeJson('build-info.json', buildInfo, { spaces: 2 });
    console.log('   ✅ Created build info file');

    console.log('🎉 Build preparation completed successfully!');
    console.log(`   📁 Temp build directory: ${tempBuildPath}`);
    console.log(`   📁 Assets directory: ${assetsPath}`);
    console.log(`   📦 Ready to build installer`);

  } catch (error) {
    console.error('❌ Build preparation failed:', error);

    // Cleanup on failure
    try {
      if (await fs.pathExists('temp-build')) {
        await fs.remove('temp-build');
        console.log('   🧹 Cleaned up temp-build directory');
      }
    } catch (cleanupError) {
      console.error('Failed to cleanup:', cleanupError);
    }

    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  prepareBuild();
}

module.exports = prepareBuild;