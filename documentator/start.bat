@echo off
echo Documentator - System for automated documentation generation
echo.

:: Check if Node.js is installed
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js version:
node -v

echo.
echo Building TypeScript...
call npx tsc --build

if %errorlevel% neq 0 (
    echo ERROR: TypeScript compilation failed
    pause
    exit /b 1
)

echo.
echo Starting Documentator MCP Server...
echo.
node dist/index.js %*