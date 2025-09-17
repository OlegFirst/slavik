@echo off
REM Digital Office Hub Installer Build Script
REM Builds the installer exe from source

echo Digital Office Hub - Installer Build
echo ====================================

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Copying main project files...
REM Copy necessary files from main project
if not exist "temp-build" mkdir temp-build
xcopy /E /Y "..\src" "temp-build\src\"
xcopy /Y "..\package.json" "temp-build\"
xcopy /Y "..\tsconfig.json" "temp-build\"
if exist "..\README.md" xcopy /Y "..\README.md" "temp-build\"

echo.
echo [3/4] Building installer executable...
call npm run build:installer
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to build installer
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo [4/4] Cleaning up temporary files...
if exist "temp-build" rmdir /S /Q "temp-build"

echo.
echo ✅ Build completed successfully!
echo.
echo The installer executable has been created in the 'dist' folder.
echo You can distribute this file to install Digital Office Hub on other computers.
echo.

if exist "dist\Digital Office Hub Setup.exe" (
    echo Installer location: dist\Digital Office Hub Setup.exe
    echo File size:
    dir "dist\Digital Office Hub Setup.exe" | findstr "Digital Office Hub Setup.exe"
) else (
    echo WARNING: Installer file not found in expected location
)

echo.
pause