@echo off
REM Installation script for Windows (Batch)
REM This script installs Chrome, sets up a virtual environment, and installs dependencies

REM Get the directory where this script is located and change to project root
cd /d "%~dp0\.."

echo =========================================
echo Wellfound Automation - Installation Script
echo =========================================
echo Working directory: %CD%
echo.

REM Step 1: Check and install Chrome
echo Step 1: Checking for Chrome...
set CHROME_FOUND=0

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    echo [OK] Chrome is already installed
    set CHROME_FOUND=1
    goto :chrome_check_done
)

if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    echo [OK] Chrome is already installed
    set CHROME_FOUND=1
    goto :chrome_check_done
)

if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    echo [OK] Chrome is already installed
    set CHROME_FOUND=1
    goto :chrome_check_done
)

:chrome_check_done
if %CHROME_FOUND%==0 (
    echo Chrome not found. Please install Chrome manually:
    echo   1. Download from: https://www.google.com/chrome/
    echo   2. Or use Chocolatey: choco install googlechrome -y
    echo.
    pause
)
echo.

REM Step 2: Check for Python
echo Step 2: Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3 from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo.

REM Step 3: Check for pip
echo Step 3: Checking for pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found. Installing pip...
    python -m ensurepip --upgrade
)
echo [OK] pip is available
echo.

REM Step 4: Create virtual environment
echo Step 4: Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment 'venv' already exists
    set /p response="Do you want to remove it and create a new one? (y/N): "
    if /i "%response%"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Created new virtual environment
    ) else (
        echo [OK] Using existing virtual environment
    )
) else (
    python -m venv venv
    echo [OK] Created virtual environment
)
echo.

REM Step 5: Install requirements
echo Step 5: Installing Python dependencies...

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Could not activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
if exist "requirements.txt" (
    echo Installing packages from requirements.txt...
    pip install -r requirements.txt
    echo [OK] All dependencies installed
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)
echo.

REM Step 6: Create .env file
echo Step 6: Setting up environment file...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] Created .env file from .env.example
        echo [WARNING] Please edit .env file with your credentials before running the script
    ) else (
        echo [WARNING] .env.example not found. Please create .env file manually
    )
) else (
    echo [OK] .env file already exists
)
echo.

echo =========================================
echo Installation Complete! 
echo =========================================
echo.
echo Next steps:
echo 1. Edit .env file with your credentials:
echo    - WELLFOUND_EMAIL
echo    - WELLFOUND_PASSWORD
echo    - RESEND_API_KEY (optional, for email reports)
echo.
echo 2. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 3. Run the script:
echo    .\run.bat
echo    or
echo    python -u main.py
echo.
pause

