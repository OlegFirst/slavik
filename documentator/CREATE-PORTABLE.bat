@echo off
title Create Digital Office Portable
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     📦 Creating Digital Office Portable Version...        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0create-portable.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to create portable version!
    pause
    exit /b 1
)

echo.
pause
