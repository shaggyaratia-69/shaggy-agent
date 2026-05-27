# Shaggy Agent Windows Installer
# Run from PowerShell inside the unzipped shaggy-agent folder:
#   Set-ExecutionPolicy -Scope Process Bypass -Force
#   .\install-shaggy-agent-windows.ps1

param(
    [string]$InstallRoot = "$env:LOCALAPPDATA\ShaggyAgent",
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Info($m) { Write-Host "-> $m" -ForegroundColor Cyan }
function Ok($m) { Write-Host "[OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }

$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $InstallRoot ".venv"
$BinDir = Join-Path $InstallRoot "bin"
$DataDir = Join-Path $InstallRoot "data"

Write-Host ""
Write-Host "+---------------------------------------------------------+" -ForegroundColor Magenta
Write-Host "|                  Shaggy Agent Installer                |" -ForegroundColor Magenta
Write-Host "+---------------------------------------------------------+" -ForegroundColor Magenta
Write-Host "|  Branded local agent based on the Shaggy Agent engine.  |" -ForegroundColor Magenta
Write-Host "+---------------------------------------------------------+" -ForegroundColor Magenta
Write-Host ""

Info "Source folder: $SourceDir"
Info "Install folder: $InstallRoot"

New-Item -ItemType Directory -Force -Path $InstallRoot, $BinDir, $DataDir | Out-Null

# Keep Shaggy Agent data separate from any Shaggy installation on the laptop.
[Environment]::SetEnvironmentVariable("SHAGGY_HOME", $DataDir, "User")
[Environment]::SetEnvironmentVariable("SHAGGY_PRODUCT_DIR", $SourceDir, "User")
$env:SHAGGY_HOME = $DataDir
$env:SHAGGY_PRODUCT_DIR = $SourceDir

# Install uv if missing.
$uv = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uv) {
    Info "Installing uv Python package manager..."
    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $possibleUv = Join-Path $env:USERPROFILE ".local\bin\uv.exe"
    if (Test-Path $possibleUv) {
        $env:Path = (Split-Path $possibleUv -Parent) + ";" + $env:Path
    }
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if (-not $uv) { throw "uv install finished, but uv.exe was not found. Restart PowerShell and run this installer again." }
}
Ok "uv found: $($uv.Source)"

Info "Installing Python 3.11 if needed..."
uv python install 3.11

if (-not (Test-Path $VenvDir)) {
    Info "Creating virtual environment..."
    uv venv $VenvDir --python 3.11
} else {
    Info "Using existing virtual environment..."
}

$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $PythonExe)) { throw "Python executable not found at $PythonExe" }

$Wheel = Get-ChildItem -Path (Join-Path $SourceDir "dist") -Filter "shaggy_agent-*.whl" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($Wheel) {
    Info "Installing Shaggy Agent from bundled wheel: $($Wheel.Name)"
    uv pip install --python $PythonExe $Wheel.FullName
} else {
    Info "Installing Shaggy Agent from local source..."
    uv pip install --python $PythonExe -e "$SourceDir[cli,pty,google,web,youtube]"
}

$ShaggyExe = Join-Path $VenvDir "Scripts\shaggy.exe"
if (-not (Test-Path $ShaggyExe)) { throw "shaggy.exe was not created. Install failed." }

# Create stable wrapper command that always uses this data folder.
$CmdPath = Join-Path $BinDir "shaggy.cmd"
$Cmd = @"
@echo off
set "SHAGGY_HOME=$DataDir"
set "SHAGGY_PRODUCT_DIR=$SourceDir"
"$ShaggyExe" %*
"@
Set-Content -Path $CmdPath -Value $Cmd -Encoding ASCII

$AgentCmdPath = Join-Path $BinDir "shaggy-agent.cmd"
$AgentCmd = @"
@echo off
set "SHAGGY_HOME=$DataDir"
set "SHAGGY_PRODUCT_DIR=$SourceDir"
"$ShaggyExe" %*
"@
Set-Content -Path $AgentCmdPath -Value $AgentCmd -Encoding ASCII

# Add bin directory to user PATH if missing.
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
if (($userPath -split ';') -notcontains $BinDir) {
    [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(';') + ";" + $BinDir).TrimStart(';'), "User")
    Warn "Added $BinDir to user PATH. Open a new PowerShell window if 'shaggy' is not found immediately."
    $env:Path = $BinDir + ";" + $env:Path
}

Ok "Shaggy Agent installed."
Info "Version check:"
& $CmdPath --version

if (-not $SkipSetup) {
    Write-Host ""
    Warn "Next step: run setup to add your model/API keys."
    Write-Host "  shaggy setup" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "Setup skipped. Run 'shaggy setup' later." -ForegroundColor Yellow
}

Write-Host "Commands:" -ForegroundColor Green
Write-Host "  shaggy" -ForegroundColor Green
Write-Host "  shaggy setup" -ForegroundColor Green
Write-Host "  shaggy doctor" -ForegroundColor Green
Write-Host ""
