@echo off
title Digital Office Installer
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║          🚀 Digital Office Installer v1.0                 ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Запуск PowerShell скрипта з правами адміністратора
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Встановлення не вдалося!
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Встановлення завершено!
echo.
pause
