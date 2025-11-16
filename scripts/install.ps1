# Installation script for Windows (PowerShell)
# This script installs Chrome, sets up a virtual environment, and installs dependencies

# Get the directory where this script is located and change to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Wellfound Automation - Installation Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Gray
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Step 1: Check and install Chrome
Write-Host "Step 1: Checking for Chrome..." -ForegroundColor Yellow
$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
)

$chromeFound = $false
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        Write-Host "✓ Chrome is already installed at: $path" -ForegroundColor Green
        $chromeFound = $true
        break
    }
}

if (-not $chromeFound) {
    Write-Host "Chrome not found. Installing Chrome..." -ForegroundColor Yellow
    
    # Check if Chocolatey is available
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Host "Installing Chrome via Chocolatey..." -ForegroundColor Yellow
        if ($isAdmin) {
            choco install googlechrome -y
        } else {
            Write-Host "⚠ Administrator rights required for Chocolatey installation" -ForegroundColor Red
            Write-Host "Please run this script as Administrator, or install Chrome manually:" -ForegroundColor Yellow
            Write-Host "  Download from: https://www.google.com/chrome/" -ForegroundColor Yellow
            $continue = Read-Host "Press Enter to continue (you can install Chrome later)"
        }
    } else {
        Write-Host "⚠ Chocolatey not found. Please install Chrome manually:" -ForegroundColor Yellow
        Write-Host "  1. Download from: https://www.google.com/chrome/" -ForegroundColor Yellow
        Write-Host "  2. Or install Chocolatey first: https://chocolatey.org/install" -ForegroundColor Yellow
        $continue = Read-Host "Press Enter to continue (you can install Chrome later)"
    }
}
Write-Host ""

# Step 2: Check for Python
Write-Host "Step 2: Checking for Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3 from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 3: Check for pip
Write-Host "Step 3: Checking for pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ pip is available" -ForegroundColor Green
} catch {
    Write-Host "⚠ pip not found. Installing pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}
Write-Host ""

# Step 4: Create virtual environment
Write-Host "Step 4: Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠ Virtual environment 'venv' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove it and create a new one? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "✓ Created new virtual environment" -ForegroundColor Green
    } else {
        Write-Host "✓ Using existing virtual environment" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "✓ Created virtual environment" -ForegroundColor Green
}
Write-Host ""

# Step 5: Install requirements
Write-Host "Step 5: Installing Python dependencies..." -ForegroundColor Yellow

# Activate virtual environment
$activateScript = "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "❌ Could not find virtual environment activation script" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install requirements
if (Test-Path "requirements.txt") {
    Write-Host "Installing packages from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "✓ All dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ requirements.txt not found!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Create .env file
Write-Host "Step 6: Setting up environment file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env file from .env.example" -ForegroundColor Green
        Write-Host "⚠ Please edit .env file with your credentials before running the script" -ForegroundColor Yellow
    } else {
        Write-Host "⚠ .env.example not found. Please create .env file manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Installation Complete! 🎉" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your credentials:" -ForegroundColor White
Write-Host "   - WELLFOUND_EMAIL" -ForegroundColor Gray
Write-Host "   - WELLFOUND_PASSWORD" -ForegroundColor Gray
Write-Host "   - RESEND_API_KEY (optional, for email reports)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Activate the virtual environment:" -ForegroundColor White
Write-Host "   venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run the script:" -ForegroundColor White
Write-Host "   .\run.ps1" -ForegroundColor Gray
Write-Host "   or" -ForegroundColor Gray
Write-Host "   python -u main.py" -ForegroundColor Gray
Write-Host ""

