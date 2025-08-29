@echo off
echo.
echo  ____                                   _        _             
echo ^|  _ \  ___   ___ _   _ _ __ ___   ___ _ ^| ^|_ __ _^| ^|_ ___  _ __ 
echo ^| ^|_) ^|/ _ \ / __^| ^| ^| ^| '_ ` _ \ / _ \ ^| ^| __/ _` ^| __/ _ \^| '__^|
echo ^|  _ ^<^| (_) ^| (__^| ^|_^| ^| ^| ^| ^| ^| ^|  __/ ^| ^| ^|^| (_^| ^| ^|^| (_) ^| ^|   
echo ^|_^| \_\\___/ \___^|\__,_^|_^| ^|_^| ^|_^|\___^|_^| ^|\__\__,_^|\__\___/^|_^|   
echo.
echo One-Click Installer for Claude Desktop
echo =====================================
echo.

REM Check if Node.js is installed
echo Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed!
    echo.
    echo Please install Node.js first:
    echo https://nodejs.org/en/download/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js found
echo.

REM First build the project
echo Building Documentator...
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

call npm run build
if %errorlevel% neq 0 (
    echo ❌ Failed to build project
    pause
    exit /b 1
)

REM Run the simple installer
echo.
echo Starting installation...
echo.

node "%~dp0simple-install.js"

if %errorlevel% equ 0 (
    echo.
    echo 🎉 SUCCESS! Documentator is ready to use
    echo.
) else (
    echo.
    echo ❌ Installation encountered issues
    echo Check the output above for details
    echo.
)

pause