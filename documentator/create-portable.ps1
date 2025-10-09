# Create Portable Version of Digital Office
# Створює портативну версію Digital Office у вигляді ZIP архіву

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     📦 Creating Digital Office Portable Version...        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Build the project
Write-Host "🔨 Building project..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build complete" -ForegroundColor Green

# Create release folder
$releasePath = ".\release-portable"
if (Test-Path $releasePath) {
    Remove-Item -Path $releasePath -Recurse -Force
}
New-Item -ItemType Directory -Path $releasePath -Force | Out-Null

# Copy necessary files
Write-Host ""
Write-Host "📂 Copying files..." -ForegroundColor Yellow

$filesToCopy = @(
    "dist",
    "data",
    "src\agents",
    "package.json",
    "package-lock.json",
    "INSTALLATION.md",
    "README.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $releasePath -Recurse -Force
    }
}

# Create batch files in portable version
Write-Host "🔧 Creating launch scripts..." -ForegroundColor Yellow

# Setup Wizard
$setupBat = @"
@echo off
title Digital Office Setup Wizard
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          🚀 Digital Office Setup Wizard                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    call npm install --production
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
)

node dist\cli\setup-wizard.js
pause
"@
Set-Content -Path "$releasePath\Setup-Wizard.bat" -Value $setupBat

# Start Hub
$hubBat = @"
@echo off
title Digital Office Hub
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          🚀 Digital Office Hub                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    call npm install --production
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
)

node dist\index-new.js hub
pause
"@
Set-Content -Path "$releasePath\Start-Hub.bat" -Value $hubBat

# First Run batch
$firstRunBat = @"
@echo off
title Digital Office - First Run Setup
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          🚀 Digital Office - First Run Setup              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📋 Checking Node.js...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found!
    echo.
    echo Please install Node.js 18+ from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js found
echo.
echo 📦 Installing dependencies...
call npm install --production

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ✅ Installation complete!
echo.
echo Next steps:
echo   1. Double-click "Setup-Wizard.bat" to configure Email and Asana
echo   2. Double-click "Start-Hub.bat" to launch Digital Office Hub
echo.
pause
"@
Set-Content -Path "$releasePath\FIRST-RUN.bat" -Value $firstRunBat

# Create README for portable version
$portableReadme = @"
# Digital Office - Portable Version

## Quick Start

### First Time Setup:
1. Double-click **FIRST-RUN.bat** to install dependencies
2. Double-click **Setup-Wizard.bat** to configure Email and Asana
3. Double-click **Start-Hub.bat** to launch Digital Office Hub

### Requirements:
- Node.js 18+ (https://nodejs.org/)
- Windows 10/11 64-bit
- 4 GB RAM minimum

### Files:
- **FIRST-RUN.bat** - First time setup (installs dependencies)
- **Setup-Wizard.bat** - Configure Email and Asana
- **Start-Hub.bat** - Launch Digital Office Hub
- **INSTALLATION.md** - Full installation guide

### Configuration Files:
- Email: data/config/email-credentials.json
- Asana: data/integrations/config.json

### Email Digest Agent:
Runs daily at 16:00 Kyiv time
- Analyzes inbox
- Creates Asana tasks for important emails
- Sends daily digest
- Collects meeting summaries from Otter.ai, Read.ai, etc.

For more information, see INSTALLATION.md

---
Digital Office v1.0
"@
Set-Content -Path "$releasePath\README-PORTABLE.txt" -Value $portableReadme

Write-Host "✅ Launch scripts created" -ForegroundColor Green

# Create ZIP archive
Write-Host ""
Write-Host "📦 Creating ZIP archive..." -ForegroundColor Yellow
$zipPath = ".\DigitalOffice-Portable-v1.0.zip"
if (Test-Path $zipPath) {
    Remove-Item -Path $zipPath -Force
}

Compress-Archive -Path "$releasePath\*" -DestinationPath $zipPath -Force
Write-Host "✅ ZIP archive created: $zipPath" -ForegroundColor Green

# Cleanup
Write-Host ""
Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
Remove-Item -Path $releasePath -Recurse -Force
Write-Host "✅ Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          ✅ Portable version created successfully!        ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📦 File: $zipPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Distribution instructions:" -ForegroundColor Yellow
Write-Host "  1. Share the ZIP file with users" -ForegroundColor White
Write-Host "  2. Users extract to any folder" -ForegroundColor White
Write-Host "  3. Users run FIRST-RUN.bat" -ForegroundColor White
Write-Host "  4. Users run Setup-Wizard.bat to configure" -ForegroundColor White
Write-Host "  5. Users run Start-Hub.bat to launch" -ForegroundColor White
Write-Host ""
