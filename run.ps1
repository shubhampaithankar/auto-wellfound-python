# Windows PowerShell script to run the Wellfound automation script
# This script activates the virtual environment and runs main.py

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run the installation script first:" -ForegroundColor Yellow
    Write-Host "  .\scripts\install.ps1" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Run the Python script with unbuffered output
python -u main.py $args

# Deactivate virtual environment (optional, happens automatically when script exits)
deactivate

