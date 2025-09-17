# Digital Office Hub - System Requirements Check
# Перевірка системних вимог перед встановленням

Write-Host "Digital Office Hub - System Requirements Check" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

$results = @{
    OS = @{ Status = "Unknown"; Details = ""; Required = $true }
    Architecture = @{ Status = "Unknown"; Details = ""; Required = $true }
    DiskSpace = @{ Status = "Unknown"; Details = ""; Required = $true }
    Memory = @{ Status = "Unknown"; Details = ""; Required = $true }
    NodeJS = @{ Status = "Unknown"; Details = ""; Required = $true }
    NPM = @{ Status = "Unknown"; Details = ""; Required = $true }
    Git = @{ Status = "Unknown"; Details = ""; Required = $false }
    PowerShell = @{ Status = "Unknown"; Details = ""; Required = $true }
    ClaudeDesktop = @{ Status = "Unknown"; Details = ""; Required = $false }
    InternetConnection = @{ Status = "Unknown"; Details = ""; Required = $true }
}

# Функція перевірки операційної системи
function Test-OperatingSystem {
    Write-Host "🔍 Перевірка операційної системи..." -ForegroundColor Blue

    $os = Get-WmiObject -Class Win32_OperatingSystem
    $osVersion = [System.Environment]::OSVersion.Version

    if ($osVersion.Major -ge 10) {
        $results.OS.Status = "OK"
        $results.OS.Details = "$($os.Caption) (Build $($os.BuildNumber))"
        Write-Host "✅ ОС: $($results.OS.Details)" -ForegroundColor Green
    }
    elseif ($osVersion.Major -eq 6 -and $osVersion.Minor -ge 1) {
        $results.OS.Status = "Warning"
        $results.OS.Details = "$($os.Caption) (не рекомендується)"
        Write-Host "⚠️  ОС: $($results.OS.Details)" -ForegroundColor Yellow
    }
    else {
        $results.OS.Status = "Error"
        $results.OS.Details = "$($os.Caption) (не підтримується)"
        Write-Host "❌ ОС: $($results.OS.Details)" -ForegroundColor Red
    }
}

# Функція перевірки архітектури
function Test-Architecture {
    Write-Host "🔍 Перевірка архітектури процесора..." -ForegroundColor Blue

    $arch = [System.Environment]::GetEnvironmentVariable("PROCESSOR_ARCHITECTURE")

    if ($arch -eq "AMD64" -or $arch -eq "x64") {
        $results.Architecture.Status = "OK"
        $results.Architecture.Details = "64-bit"
        Write-Host "✅ Архітектура: 64-bit" -ForegroundColor Green
    }
    elseif ($arch -eq "x86") {
        $results.Architecture.Status = "Warning"
        $results.Architecture.Details = "32-bit (обмежена підтримка)"
        Write-Host "⚠️  Архітектура: 32-bit (обмежена підтримка)" -ForegroundColor Yellow
    }
    else {
        $results.Architecture.Status = "Error"
        $results.Architecture.Details = "$arch (не підтримується)"
        Write-Host "❌ Архітектура: $arch (не підтримується)" -ForegroundColor Red
    }
}

# Функція перевірки дискового простору
function Test-DiskSpace {
    Write-Host "🔍 Перевірка вільного місця на диску..." -ForegroundColor Blue

    try {
        $systemDrive = [System.Environment]::GetEnvironmentVariable("SystemDrive")
        $drive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $systemDrive }

        $freeSpaceGB = [math]::Round($drive.FreeSpace / 1GB, 2)
        $totalSpaceGB = [math]::Round($drive.Size / 1GB, 2)
        $requiredGB = 1.0  # Мінімум 1GB

        if ($freeSpaceGB -ge $requiredGB) {
            $results.DiskSpace.Status = "OK"
            $results.DiskSpace.Details = "$freeSpaceGB GB вільно з $totalSpaceGB GB"
            Write-Host "✅ Дисковий простір: $($results.DiskSpace.Details)" -ForegroundColor Green
        }
        else {
            $results.DiskSpace.Status = "Error"
            $results.DiskSpace.Details = "$freeSpaceGB GB вільно (потрібно $requiredGB GB)"
            Write-Host "❌ Дисковий простір: $($results.DiskSpace.Details)" -ForegroundColor Red
        }
    }
    catch {
        $results.DiskSpace.Status = "Error"
        $results.DiskSpace.Details = "Помилка перевірки"
        Write-Host "❌ Помилка перевірки дискового простору" -ForegroundColor Red
    }
}

# Функція перевірки пам'яті
function Test-Memory {
    Write-Host "🔍 Перевірка оперативної пам'яті..." -ForegroundColor Blue

    try {
        $memory = Get-WmiObject -Class Win32_ComputerSystem
        $totalMemoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
        $requiredGB = 2.0  # Мінімум 2GB

        if ($totalMemoryGB -ge $requiredGB) {
            $results.Memory.Status = "OK"
            $results.Memory.Details = "$totalMemoryGB GB"
            Write-Host "✅ Оперативна пам'ять: $totalMemoryGB GB" -ForegroundColor Green
        }
        elseif ($totalMemoryGB -ge 1.0) {
            $results.Memory.Status = "Warning"
            $results.Memory.Details = "$totalMemoryGB GB (рекомендується $requiredGB GB)"
            Write-Host "⚠️  Оперативна пам'ять: $totalMemoryGB GB (рекомендується $requiredGB GB)" -ForegroundColor Yellow
        }
        else {
            $results.Memory.Status = "Error"
            $results.Memory.Details = "$totalMemoryGB GB (недостатньо)"
            Write-Host "❌ Оперативна пам'ять: $totalMemoryGB GB (недостатньо)" -ForegroundColor Red
        }
    }
    catch {
        $results.Memory.Status = "Error"
        $results.Memory.Details = "Помилка перевірки"
        Write-Host "❌ Помилка перевірки пам'яті" -ForegroundColor Red
    }
}

# Функція перевірки Node.js
function Test-NodeJS {
    Write-Host "🔍 Перевірка Node.js..." -ForegroundColor Blue

    try {
        $nodeVersion = & node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $versionNumber = $nodeVersion -replace 'v', ''
            $majorVersion = [int]($versionNumber.Split('.')[0])

            if ($majorVersion -ge 18) {
                $results.NodeJS.Status = "OK"
                $results.NodeJS.Details = $nodeVersion
                Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
            }
            elseif ($majorVersion -ge 16) {
                $results.NodeJS.Status = "Warning"
                $results.NodeJS.Details = "$nodeVersion (рекомендується v18+)"
                Write-Host "⚠️  Node.js: $nodeVersion (рекомендується v18+)" -ForegroundColor Yellow
            }
            else {
                $results.NodeJS.Status = "Error"
                $results.NodeJS.Details = "$nodeVersion (застаріла версія)"
                Write-Host "❌ Node.js: $nodeVersion (застаріла версія)" -ForegroundColor Red
            }
        }
        else {
            $results.NodeJS.Status = "Error"
            $results.NodeJS.Details = "Не встановлено"
            Write-Host "❌ Node.js не встановлено" -ForegroundColor Red
        }
    }
    catch {
        $results.NodeJS.Status = "Error"
        $results.NodeJS.Details = "Помилка перевірки"
        Write-Host "❌ Помилка перевірки Node.js" -ForegroundColor Red
    }
}

# Функція перевірки NPM
function Test-NPM {
    Write-Host "🔍 Перевірка NPM..." -ForegroundColor Blue

    try {
        $npmVersion = & npm --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $results.NPM.Status = "OK"
            $results.NPM.Details = "v$npmVersion"
            Write-Host "✅ NPM: v$npmVersion" -ForegroundColor Green
        }
        else {
            $results.NPM.Status = "Error"
            $results.NPM.Details = "Не встановлено"
            Write-Host "❌ NPM не встановлено" -ForegroundColor Red
        }
    }
    catch {
        $results.NPM.Status = "Error"
        $results.NPM.Details = "Помилка перевірки"
        Write-Host "❌ Помилка перевірки NPM" -ForegroundColor Red
    }
}

# Функція перевірки Git
function Test-Git {
    Write-Host "🔍 Перевірка Git..." -ForegroundColor Blue

    try {
        $gitVersion = & git --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $results.Git.Status = "OK"
            $results.Git.Details = $gitVersion
            Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
        }
        else {
            $results.Git.Status = "Warning"
            $results.Git.Details = "Не встановлено (опціонально)"
            Write-Host "⚠️  Git не встановлено (опціонально для розробки)" -ForegroundColor Yellow
        }
    }
    catch {
        $results.Git.Status = "Warning"
        $results.Git.Details = "Не встановлено (опціонально)"
        Write-Host "⚠️  Git не встановлено (опціонально)" -ForegroundColor Yellow
    }
}

# Функція перевірки PowerShell
function Test-PowerShellVersion {
    Write-Host "🔍 Перевірка PowerShell..." -ForegroundColor Blue

    $psVersion = $PSVersionTable.PSVersion

    if ($psVersion.Major -ge 5) {
        $results.PowerShell.Status = "OK"
        $results.PowerShell.Details = "v$($psVersion.Major).$($psVersion.Minor)"
        Write-Host "✅ PowerShell: v$($psVersion.Major).$($psVersion.Minor)" -ForegroundColor Green
    }
    else {
        $results.PowerShell.Status = "Error"
        $results.PowerShell.Details = "v$($psVersion.Major).$($psVersion.Minor) (застаріла)"
        Write-Host "❌ PowerShell: v$($psVersion.Major).$($psVersion.Minor) (потрібно v5+)" -ForegroundColor Red
    }
}

# Функція перевірки Claude Desktop
function Test-ClaudeDesktop {
    Write-Host "🔍 Перевірка Claude Desktop..." -ForegroundColor Blue

    $claudePaths = @(
        "$env:USERPROFILE\AppData\Roaming\Claude\claude_desktop_config.json",
        "$env:USERPROFILE\.claude\claude_desktop_config.json",
        "$env:LOCALAPPDATA\Claude\claude_desktop_config.json"
    )

    $found = $false
    foreach ($path in $claudePaths) {
        if (Test-Path $path) {
            $results.ClaudeDesktop.Status = "OK"
            $results.ClaudeDesktop.Details = "Знайдено конфігурацію"
            Write-Host "✅ Claude Desktop: Конфігурацію знайдено" -ForegroundColor Green
            $found = $true
            break
        }
    }

    if (-not $found) {
        $results.ClaudeDesktop.Status = "Warning"
        $results.ClaudeDesktop.Details = "Не знайдено (буде пропущено автоналаштування)"
        Write-Host "⚠️  Claude Desktop: Не знайдено (опціонально)" -ForegroundColor Yellow
    }
}

# Функція перевірки інтернет-з'єднання
function Test-InternetConnection {
    Write-Host "🔍 Перевірка інтернет-з'єднання..." -ForegroundColor Blue

    try {
        $testSites = @("google.com", "nodejs.org", "npmjs.com")
        $successful = 0

        foreach ($site in $testSites) {
            try {
                $response = Test-NetConnection -ComputerName $site -Port 80 -WarningAction SilentlyContinue
                if ($response.TcpTestSucceeded) {
                    $successful++
                }
            }
            catch {
                # Ignore individual failures
            }
        }

        if ($successful -ge 2) {
            $results.InternetConnection.Status = "OK"
            $results.InternetConnection.Details = "З'єднання встановлено"
            Write-Host "✅ Інтернет-з'єднання: Доступне" -ForegroundColor Green
        }
        elseif ($successful -ge 1) {
            $results.InternetConnection.Status = "Warning"
            $results.InternetConnection.Details = "Нестабільне з'єднання"
            Write-Host "⚠️  Інтернет-з'єднання: Нестабільне" -ForegroundColor Yellow
        }
        else {
            $results.InternetConnection.Status = "Error"
            $results.InternetConnection.Details = "Відсутнє"
            Write-Host "❌ Інтернет-з'єднання: Відсутнє" -ForegroundColor Red
        }
    }
    catch {
        $results.InternetConnection.Status = "Warning"
        $results.InternetConnection.Details = "Не вдалося перевірити"
        Write-Host "⚠️  Інтернет-з'єднання: Не вдалося перевірити" -ForegroundColor Yellow
    }
}

# Функція виведення підсумку
function Show-Summary {
    Write-Host ""
    Write-Host "📋 Підсумок перевірки системи" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan

    $criticalErrors = 0
    $warnings = 0

    foreach ($check in $results.Keys) {
        $result = $results[$check]
        $status = switch ($result.Status) {
            "OK" { "✅"; break }
            "Warning" { $warnings++; "⚠️ "; break }
            "Error" { if ($result.Required) { $criticalErrors++ }; "❌"; break }
            default { "❓"; break }
        }

        $required = if ($result.Required) { " (обов'язково)" } else { " (опціонально)" }
        Write-Host "$status $check`: $($result.Details)$required"
    }

    Write-Host ""

    if ($criticalErrors -eq 0) {
        Write-Host "🎉 Система готова для встановлення Digital Office Hub!" -ForegroundColor Green
        if ($warnings -gt 0) {
            Write-Host "⚠️  Є $warnings попереджень, але встановлення можливе" -ForegroundColor Yellow
        }
        return $true
    }
    else {
        Write-Host "❌ Знайдено $criticalErrors критичних помилок. Встановлення неможливе." -ForegroundColor Red
        Write-Host ""
        Write-Host "Рекомендації:" -ForegroundColor Cyan

        if ($results.NodeJS.Status -eq "Error") {
            Write-Host "- Встановіть Node.js v18+ з https://nodejs.org" -ForegroundColor White
        }

        if ($results.DiskSpace.Status -eq "Error") {
            Write-Host "- Звільніть місце на диску (потрібно мінімум 1GB)" -ForegroundColor White
        }

        if ($results.OS.Status -eq "Error") {
            Write-Host "- Оновіть операційну систему до Windows 10 або новішої" -ForegroundColor White
        }

        return $false
    }
}

# Експорт результатів у JSON
function Export-Results {
    param([string]$OutputPath = "system-check-results.json")

    try {
        $exportData = @{
            Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            SystemInfo = @{
                ComputerName = $env:COMPUTERNAME
                UserName = $env:USERNAME
                PowerShellVersion = "$($PSVersionTable.PSVersion.Major).$($PSVersionTable.PSVersion.Minor)"
            }
            Results = $results
        }

        $exportData | ConvertTo-Json -Depth 3 | Set-Content -Path $OutputPath -Encoding UTF8
        Write-Host "📄 Результати експортовано в: $OutputPath" -ForegroundColor Gray
    }
    catch {
        Write-Host "❌ Помилка експорту результатів: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Виконання всіх перевірок
try {
    Test-OperatingSystem
    Test-Architecture
    Test-DiskSpace
    Test-Memory
    Test-PowerShellVersion
    Test-NodeJS
    Test-NPM
    Test-Git
    Test-ClaudeDesktop
    Test-InternetConnection

    $canInstall = Show-Summary

    # Експорт результатів
    Export-Results

    # Повернення коду виходу
    if ($canInstall) {
        exit 0
    }
    else {
        exit 1
    }
}
catch {
    Write-Host "❌ Критична помилка під час перевірки системи: $($_.Exception.Message)" -ForegroundColor Red
    exit 2
}