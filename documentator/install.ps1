# Digital Office Installer
# Автоматична установка Digital Office Hub

param(
    [string]$InstallPath = "$env:LOCALAPPDATA\DigitalOffice"
)

$ErrorActionPreference = "Stop"

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "║          🚀 Digital Office Installer v1.0                 ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Перевірка чи Node.js встановлено
Write-Host "📋 Перевірка системних вимог..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    Write-Host "✅ Node.js встановлено: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js не знайдено!" -ForegroundColor Red
    Write-Host "Будь ласка, встановіть Node.js 18+ з https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Створення папки для встановлення
Write-Host ""
Write-Host "📁 Створення папки для встановлення: $InstallPath" -ForegroundColor Yellow
if (Test-Path $InstallPath) {
    $overwrite = Read-Host "Папка вже існує. Перезаписати? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Встановлення скасовано." -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Path $InstallPath -Recurse -Force
}
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
Write-Host "✅ Папка створена" -ForegroundColor Green

# Копіювання файлів
Write-Host ""
Write-Host "📦 Копіювання файлів..." -ForegroundColor Yellow
$currentPath = $PSScriptRoot
Copy-Item -Path "$currentPath\*" -Destination $InstallPath -Recurse -Force -Exclude @(".git", "node_modules", "dist", "release")
Write-Host "✅ Файли скопійовано" -ForegroundColor Green

# Встановлення npm пакетів
Write-Host ""
Write-Host "📦 Встановлення залежностей..." -ForegroundColor Yellow
Push-Location $InstallPath
npm install --production
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Помилка встановлення залежностей" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "✅ Залежності встановлено" -ForegroundColor Green

# Збірка проекту
Write-Host ""
Write-Host "🔨 Збірка проекту..." -ForegroundColor Yellow
Push-Location $InstallPath
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Помилка збірки" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "✅ Проект зібрано" -ForegroundColor Green

# Створення батників для запуску
Write-Host ""
Write-Host "🔧 Створення ярликів..." -ForegroundColor Yellow

# Setup Wizard батник
$setupBat = @"
@echo off
cd /d "$InstallPath"
node dist\cli\setup-wizard.js
pause
"@
Set-Content -Path "$InstallPath\Setup-Wizard.bat" -Value $setupBat

# Digital Office Hub батник
$hubBat = @"
@echo off
cd /d "$InstallPath"
node dist\index-new.js hub
pause
"@
Set-Content -Path "$InstallPath\Start-Hub.bat" -Value $hubBat

# Створення ярлика на робочому столі
$desktopPath = [Environment]::GetFolderPath("Desktop")
$WScriptShell = New-Object -ComObject WScript.Shell

# Ярлик для Setup Wizard
$shortcut = $WScriptShell.CreateShortcut("$desktopPath\Digital Office Setup.lnk")
$shortcut.TargetPath = "$InstallPath\Setup-Wizard.bat"
$shortcut.WorkingDirectory = $InstallPath
$shortcut.Description = "Налаштування Digital Office"
$shortcut.Save()

# Ярлик для Hub
$shortcut = $WScriptShell.CreateShortcut("$desktopPath\Digital Office Hub.lnk")
$shortcut.TargetPath = "$InstallPath\Start-Hub.bat"
$shortcut.WorkingDirectory = $InstallPath
$shortcut.Description = "Запуск Digital Office Hub"
$shortcut.Save()

Write-Host "✅ Ярлики створено на робочому столі" -ForegroundColor Green

# Створення папок для даних
Write-Host ""
Write-Host "📁 Створення папок для даних..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$InstallPath\data\config" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\data\integrations" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\data\agents" -Force | Out-Null
New-Item -ItemType Directory -Path "$InstallPath\data\store" -Force | Out-Null
Write-Host "✅ Папки створено" -ForegroundColor Green

# Завершення
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "║          ✅ Встановлення завершено успішно!               ║" -ForegroundColor Green
Write-Host "║                                                            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Встановлено в: $InstallPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Наступні кроки:" -ForegroundColor Yellow
Write-Host "  1. Подвійний клік на 'Digital Office Setup' (на робочому столі)" -ForegroundColor White
Write-Host "  2. Налаштуйте Email та Asana" -ForegroundColor White
Write-Host "  3. Подвійний клік на 'Digital Office Hub' для запуску" -ForegroundColor White
Write-Host ""
Write-Host "Дякуємо що використовуєте Digital Office! 🎉" -ForegroundColor Cyan
Write-Host ""

# Пропозиція запустити setup
$runSetup = Read-Host "Запустити Setup Wizard зараз? (y/n)"
if ($runSetup -eq "y") {
    Start-Process -FilePath "$InstallPath\Setup-Wizard.bat" -Wait
}
