$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Version = '156.0.8078.73'
$RuntimeRoot = Join-Path $PSScriptRoot '.browser'
$Destination = Join-Path $RuntimeRoot $Version

if (Test-Path $Destination) {
    foreach ($relativePath in @('chrome-win64\chrome.exe', 'chromedriver-win64\chromedriver.exe')) {
        if (-not (Test-Path (Join-Path $Destination $relativePath) -PathType Leaf)) {
            throw "Incomplete runtime at $Destination. Move it aside and run this installer again."
        }
    }
    Write-Output "Pinned runtime already installed: $Destination"
    return
}

$TemporaryRoot = Join-Path $RuntimeRoot ('install-' + [guid]::NewGuid().ToString('N'))
$Staging = Join-Path $TemporaryRoot 'runtime'
New-Item -ItemType Directory -Path $Staging -Force | Out-Null
try {
    foreach ($package in @('chrome', 'chromedriver')) {
        $archive = Join-Path $TemporaryRoot "$package-win64.zip"
        $url = "https://storage.googleapis.com/chrome-for-testing-public/$Version/win64/$package-win64.zip"
        Write-Output "Downloading $package $Version from $url"
        Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing -TimeoutSec 300
        Expand-Archive -Path $archive -DestinationPath $Staging
    }
    foreach ($relativePath in @('chrome-win64\chrome.exe', 'chromedriver-win64\chromedriver.exe')) {
        if (-not (Test-Path (Join-Path $Staging $relativePath) -PathType Leaf)) {
            throw "Downloaded runtime is missing $relativePath"
        }
    }
    $driver = Join-Path $Staging 'chromedriver-win64\chromedriver.exe'
    $driverVersion = & $driver --version
    if ($LASTEXITCODE -ne 0 -or $driverVersion -notlike "ChromeDriver $Version *") {
        throw 'Downloaded ChromeDriver version check failed.'
    }
    $chromeVersion = (Get-Item (Join-Path $Staging 'chrome-win64\chrome.exe')).VersionInfo.ProductVersion
    if ($chromeVersion -ne $Version) {
        throw "Downloaded Chrome version mismatch: $chromeVersion"
    }
    Move-Item -Path $Staging -Destination $Destination
    Write-Output "Installed pinned Chrome and ChromeDriver $Version at $Destination"
} finally {
    Remove-Item -Path $TemporaryRoot -Recurse -Force
}