# Digital Office Hub - Claude Desktop Configuration Script
# Автоматичне налаштування Claude Desktop для роботи з Digital Office Hub

param(
    [Parameter(Mandatory=$true)]
    [string]$InstallPath,

    [Parameter(Mandatory=$false)]
    [string]$ConfigPath = "",

    [Parameter(Mandatory=$false)]
    [switch]$Force = $false
)

Write-Host "Digital Office Hub - Claude Desktop Configuration" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Функція пошуку конфігурації Claude Desktop
function Find-ClaudeConfig {
    $possiblePaths = @(
        "$env:USERPROFILE\AppData\Roaming\Claude\claude_desktop_config.json",
        "$env:USERPROFILE\.claude\claude_desktop_config.json",
        "$env:LOCALAPPDATA\Claude\claude_desktop_config.json"
    )

    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            Write-Host "✅ Знайдено конфігурацію Claude Desktop: $path" -ForegroundColor Green
            return $path
        }
    }

    Write-Host "❌ Конфігурацію Claude Desktop не знайдено" -ForegroundColor Red
    Write-Host "Перевірені шляхи:" -ForegroundColor Yellow
    foreach ($path in $possiblePaths) {
        Write-Host "  - $path" -ForegroundColor Gray
    }

    return $null
}

# Функція створення backup
function Create-Backup {
    param([string]$configPath)

    $backupPath = "$configPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    try {
        Copy-Item $configPath $backupPath -Force
        Write-Host "✅ Створено backup: $backupPath" -ForegroundColor Green
        return $backupPath
    }
    catch {
        Write-Host "❌ Помилка створення backup: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Функція валідації JSON
function Test-JsonValid {
    param([string]$jsonContent)

    try {
        $jsonContent | ConvertFrom-Json | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Основна функція конфігурації
function Configure-ClaudeDesktop {
    param([string]$configPath, [string]$installPath)

    Write-Host "📝 Налаштування Claude Desktop..." -ForegroundColor Blue

    try {
        # Читаємо існуючу конфігурацію
        $configContent = Get-Content $configPath -Raw -Encoding UTF8

        # Валідуємо JSON
        if (-not (Test-JsonValid $configContent)) {
            Write-Host "❌ Некоректний JSON у файлі конфігурації" -ForegroundColor Red
            return $false
        }

        # Парсимо JSON
        $config = $configContent | ConvertFrom-Json

        # Ініціалізуємо mcpServers якщо відсутній
        if (-not $config.PSObject.Properties.Name -contains "mcpServers") {
            $config | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue @{}
        }

        # Перевіряємо чи вже налаштовано Digital Office
        if ($config.mcpServers.PSObject.Properties.Name -contains "digital-office") {
            if (-not $Force) {
                Write-Host "⚠️  Digital Office вже налаштовано в Claude Desktop" -ForegroundColor Yellow
                Write-Host "   Використайте -Force для перезапису" -ForegroundColor Yellow
                return $true
            }
            else {
                Write-Host "🔄 Перезаписуємо існуючу конфігурацію..." -ForegroundColor Yellow
            }
        }

        # Додаємо конфігурацію Digital Office Hub
        $digitalOfficeConfig = @{
            command = "node"
            args = @("$installPath\dist\index-new.js")
            env = @{
                NODE_ENV = "production"
            }
        }

        $config.mcpServers | Add-Member -NotePropertyName "digital-office" -NotePropertyValue $digitalOfficeConfig -Force

        # Конвертуємо назад у JSON з форматуванням
        $newConfigContent = $config | ConvertTo-Json -Depth 10 -Compress:$false

        # Записуємо оновлену конфігурацію
        $newConfigContent | Set-Content $configPath -Encoding UTF8

        Write-Host "✅ Claude Desktop успішно налаштовано" -ForegroundColor Green
        Write-Host "📁 Конфігурація збережена: $configPath" -ForegroundColor Gray

        return $true
    }
    catch {
        Write-Host "❌ Помилка налаштування: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Функція перевірки конфігурації
function Test-Configuration {
    param([string]$configPath)

    Write-Host "🔍 Перевірка конфігурації..." -ForegroundColor Blue

    try {
        $config = Get-Content $configPath -Raw | ConvertFrom-Json

        if ($config.mcpServers.PSObject.Properties.Name -contains "digital-office") {
            $doConfig = $config.mcpServers."digital-office"

            Write-Host "✅ Digital Office знайдено в конфігурації" -ForegroundColor Green
            Write-Host "   Command: $($doConfig.command)" -ForegroundColor Gray
            Write-Host "   Args: $($doConfig.args -join ' ')" -ForegroundColor Gray
            Write-Host "   Env: NODE_ENV=$($doConfig.env.NODE_ENV)" -ForegroundColor Gray

            # Перевіряємо чи існує файл
            $scriptPath = $doConfig.args[0]
            if (Test-Path $scriptPath) {
                Write-Host "✅ Файл скрипту знайдено: $scriptPath" -ForegroundColor Green
            }
            else {
                Write-Host "❌ Файл скрипту не знайдено: $scriptPath" -ForegroundColor Red
            }

            return $true
        }
        else {
            Write-Host "❌ Digital Office не знайдено в конфігурації" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ Помилка перевірки: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Головна логіка
try {
    # Перевіряємо шлях встановлення
    if (-not (Test-Path $InstallPath)) {
        Write-Host "❌ Шлях встановлення не знайдено: $InstallPath" -ForegroundColor Red
        exit 1
    }

    # Перевіряємо наявність скрипту Digital Office
    $scriptPath = Join-Path $InstallPath "dist\index-new.js"
    if (-not (Test-Path $scriptPath)) {
        Write-Host "❌ Скрипт Digital Office не знайдено: $scriptPath" -ForegroundColor Red
        Write-Host "   Переконайтеся що Digital Office Hub встановлено правильно" -ForegroundColor Yellow
        exit 1
    }

    # Знаходимо конфігурацію Claude Desktop
    if ([string]::IsNullOrEmpty($ConfigPath)) {
        $ConfigPath = Find-ClaudeConfig
        if ($null -eq $ConfigPath) {
            Write-Host "❌ Не вдалося знайти конфігурацію Claude Desktop" -ForegroundColor Red
            Write-Host "   Переконайтеся що Claude Desktop встановлено" -ForegroundColor Yellow
            exit 1
        }
    }
    else {
        if (-not (Test-Path $ConfigPath)) {
            Write-Host "❌ Вказаний файл конфігурації не існує: $ConfigPath" -ForegroundColor Red
            exit 1
        }
    }

    # Створюємо backup
    $backupPath = Create-Backup $ConfigPath
    if ($null -eq $backupPath) {
        Write-Host "❌ Не вдалося створити backup конфігурації" -ForegroundColor Red
        exit 1
    }

    # Виконуємо конфігурацію
    $success = Configure-ClaudeDesktop $ConfigPath $InstallPath

    if ($success) {
        # Перевіряємо результат
        if (Test-Configuration $ConfigPath) {
            Write-Host ""
            Write-Host "🎉 Налаштування завершено успішно!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Наступні кроки:" -ForegroundColor Cyan
            Write-Host "1. Перезапустіть Claude Desktop" -ForegroundColor White
            Write-Host "2. Digital Office Hub буде доступний як MCP сервер" -ForegroundColor White
            Write-Host "3. Перевірте працездатність командою в Claude:" -ForegroundColor White
            Write-Host "   'List available MCP tools'" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Backup конфігурації збережено: $backupPath" -ForegroundColor Gray
        }
        else {
            Write-Host "❌ Конфігурація створена, але перевірка не пройшла" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "❌ Помилка налаштування Claude Desktop" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Критична помилка: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Gray
    exit 1
}

exit 0