@echo off
REM Windows batch script to run the Wellfound automation script
REM This script activates the virtual environment and runs main.py

REM Get the directory where this script is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run the installation script first:
    echo   scripts\install.bat
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the Python script with unbuffered output
python -u main.py %*

REM Deactivate virtual environment (optional, happens automatically when script exits)
deactivate

