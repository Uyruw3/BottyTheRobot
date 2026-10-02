# Botty Prototype - Windows PowerShell Launcher
# Usage: .\scripts\run_botty.ps1 [options]

param(
    [switch]$Debug,
    [switch]$Windowed,
    [switch]$NoWeb,
    [switch]$Help,
    [string]$Mode = "auto"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location -LiteralPath $ProjectRoot

if ($Help) {
    Write-Host @"
Botty Prototype Launcher
Usage: .\scripts\run_botty.ps1 [options]

Options:
  -Debug      Enable debug logging
  -Windowed   Force windowed mode (BOTTY_FULLSCREEN=false)
  -NoWeb      Disable web dashboard
  -Mode       Startup mode: auto, manual, developer (default: auto)
  -Help       Show this help message

Examples:
  .\scripts\run_botty.ps1
  .\scripts\run_botty.ps1 -Debug -Mode developer
  .\scripts\run_botty.ps1 -Windowed -NoWeb
"@
    exit 0
}

# Environment variables
if ($Windowed) {
    $env:BOTTY_FULLSCREEN = "false"
}
if ($Debug) {
    $env:BOTTY_DEBUG = "1"
}
if ($NoWeb) {
    $env:BOTTY_WEB_ENABLED = "0"
}
$env:BOTTY_MODE = $Mode

Write-Host "=== Botty Prototype v0.1.0 ===" -ForegroundColor Cyan
Write-Host "Mode: $Mode" -ForegroundColor Yellow
Write-Host "Debug: $(if($Debug){'ON'}else{'OFF'})" -ForegroundColor Yellow
Write-Host "Fullscreen: $(if($Windowed){'OFF'}else{'ON'})" -ForegroundColor Yellow
Write-Host "Web: $(if($NoWeb){'OFF'}else{'ON'})" -ForegroundColor Yellow
Write-Host "Starting Botty..." -ForegroundColor Green

# Check Python version
$pyVersion = & python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Install Python 3.12+" -ForegroundColor Red
    exit 1
}
Write-Host "Using $pyVersion" -ForegroundColor Gray

# Check for virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Gray
    . .\.venv\Scripts\Activate.ps1
}

# Run Botty
Write-Host "Running: python -m botty" -ForegroundColor Green
python -m botty

exit $LASTEXITCODE
