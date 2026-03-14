# ===================================================================
# Windows 任务计划程序自动配置脚本
# ===================================================================
# 此脚本会在 Windows 任务计划程序中创建一个定时任务
# 使用方法：以管理员身份运行 PowerShell，然后执行此脚本
# ===================================================================

# 任务配置
$TaskName = "BUAA_场地预约"
$Description = "北航场地预约自动运行任务"
$ScriptPath = $PSScriptRoot
$PythonScript = Join-Path $ScriptPath "cgyy.py"
$CondaPath = "D:\anaconda"
$CondaEnv = "torch"

# 运行间隔（分钟）
$IntervalMinutes = 15

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows 任务计划程序配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "任务名称: $TaskName" -ForegroundColor Green
Write-Host "脚本路径: $PythonScript" -ForegroundColor Green
Write-Host "运行间隔: $IntervalMinutes 分钟" -ForegroundColor Green
Write-Host ""

# 检查是否以管理员身份运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "错误：请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host "右键点击 PowerShell，选择 '以管理员身份运行'" -ForegroundColor Yellow
    pause
    exit 1
}

# 删除已存在的同名任务
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "发现已存在的任务，正在删除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 创建批处理文件来运行 Python 脚本
$BatchFile = Join-Path $ScriptPath "run_scheduled.bat"
$BatchContent = @"
@echo off
chcp 65001 >nul
cd /d "$ScriptPath"

set "LOG_DIR=$ScriptPath\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set "LOG_FILE=%LOG_DIR%\cgyy.log"
set "CONDA_PATH=$CondaPath"
set "CONDA_ENV=$CondaEnv"
set "PYTHON_EXE=%CONDA_PATH%\envs\%CONDA_ENV%\python.exe"

echo ======================================== > "%LOG_FILE%"
echo [%date% %time%] 定时任务开始执行 >> "%LOG_FILE%"
echo ======================================== >> "%LOG_FILE%"

if exist "%PYTHON_EXE%" (
    echo 使用解释器: %PYTHON_EXE% >> "%LOG_FILE%"
    "%PYTHON_EXE%" "$PythonScript" >> "%LOG_FILE%" 2>&1
) else (
    echo [错误] 未找到解释器: %PYTHON_EXE% >> "%LOG_FILE%"
    echo 尝试使用 conda run 运行... >> "%LOG_FILE%"
    call "%CONDA_PATH%\condabin\conda.bat" run -n %CONDA_ENV% python "$PythonScript" >> "%LOG_FILE%" 2>&1
)

set "EXIT_CODE=%ERRORLEVEL%"
echo ---------------------------------------- >> "%LOG_FILE%"
echo [%date% %time%] 执行结束，退出码: %EXIT_CODE% >> "%LOG_FILE%"
echo ---------------------------------------- >> "%LOG_FILE%"
exit /b %EXIT_CODE%
"@
Set-Content -Path $BatchFile -Value $BatchContent -Encoding Default

# 创建日志查看脚本（用于查询上次打印信息）
$ViewLogScript = Join-Path $ScriptPath "view_last_log.ps1"
$ViewLogContent = @"
param(
    [int]
    `$Tail = 120
)

`$LogDir = Join-Path `$PSScriptRoot "logs"
`$LatestLog = Join-Path `$LogDir "cgyy.log"

if (-not (Test-Path `$LogDir)) {
    Write-Host "未找到日志目录：`$LogDir" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path `$LatestLog)) {
    Write-Host "未找到日志文件：`$LatestLog" -ForegroundColor Yellow
    exit 1
}

Write-Host "显示最近一次运行日志：`$LatestLog" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Get-Content -Path `$LatestLog -Tail `$Tail
"@
Set-Content -Path $ViewLogScript -Value $ViewLogContent -Encoding UTF8

Write-Host "创建任务中..." -ForegroundColor Green

# 创建多个触发器
# 触发器1: 开机时启动（延迟1分钟避免开机卡顿）
$trigger1 = New-ScheduledTaskTrigger -AtStartup
$trigger1.Delay = "PT1M"  # 开机后延迟1分钟启动
$trigger1.Repetition = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) | Select-Object -ExpandProperty Repetition
$trigger1.Repetition.Duration = "" # 无限期重复

# 触发器2: 每天早上7点启动（以防万一）
$trigger2 = New-ScheduledTaskTrigger -Daily -At "07:00"
$trigger2.Repetition = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) | Select-Object -ExpandProperty Repetition
$trigger2.Repetition.Duration = "" # 无限期重复

$triggers = @($trigger1, $trigger2)

# 创建操作
$action = New-ScheduledTaskAction -Execute $BatchFile

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# 获取当前用户
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

# 注册任务
Register-ScheduledTask -TaskName $TaskName -Trigger $triggers -Action $action -Settings $settings -Principal $principal -Description $Description

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "任务创建成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "任务详情：" -ForegroundColor Yellow
Write-Host "- 任务名称：$TaskName" -ForegroundColor White
Write-Host "- 运行间隔：每 $IntervalMinutes 分钟" -ForegroundColor White
Write-Host "- 开机启动：是（延迟1分钟后启动）" -ForegroundColor White
Write-Host "- 定时启动：每天 07:00" -ForegroundColor White
Write-Host "- 任务状态：已创建并启用" -ForegroundColor White
Write-Host "- 日志目录：$ScriptPath\logs" -ForegroundColor White
Write-Host ""
Write-Host "管理任务：" -ForegroundColor Yellow
Write-Host "- 查看状态：Get-ScheduledTask -TaskName '$TaskName' | Select-Object TaskName, State" -ForegroundColor White
Write-Host "- 查看详情：Get-ScheduledTaskInfo -TaskName '$TaskName'" -ForegroundColor White
Write-Host "- 启动任务：Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host "- 停止任务：Stop-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host "- 禁用任务：Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host "- 启用任务：Enable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host "- 删除任务：Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor White
Write-Host "- 查看上次日志：powershell -ExecutionPolicy Bypass -File '$ViewLogScript'" -ForegroundColor White
Write-Host "- 图形界面：按 Win+R 输入 taskschd.msc 打开任务计划程序" -ForegroundColor White
Write-Host ""
Write-Host "状态说明：" -ForegroundColor Yellow
Write-Host "- Ready   = 就绪，等待下次运行" -ForegroundColor White
Write-Host "- Running = 正在运行中" -ForegroundColor White
Write-Host "- Disabled = 已禁用" -ForegroundColor White
Write-Host ""

# 创建后立即执行一次
Start-ScheduledTask -TaskName $TaskName
Write-Host "已立即触发一次任务执行。" -ForegroundColor Green
Write-Host "稍等 10-30 秒后可查看日志：" -ForegroundColor Cyan
Write-Host "powershell -ExecutionPolicy Bypass -File '$ViewLogScript'" -ForegroundColor White
Write-Host ""

pause
