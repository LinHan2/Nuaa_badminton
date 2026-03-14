param(
    [int]
    $Tail = 120
)

$LogDir = Join-Path $PSScriptRoot "logs"
$LatestLog = Join-Path $LogDir "cgyy.log"

if (-not (Test-Path $LogDir)) {
    Write-Host "未找到日志目录：$LogDir" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $LatestLog)) {
    Write-Host "未找到日志文件：$LatestLog" -ForegroundColor Yellow
    exit 1
}

Write-Host "显示最近一次运行日志：$LatestLog" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor DarkGray
Get-Content -Path $LatestLog -Tail $Tail
