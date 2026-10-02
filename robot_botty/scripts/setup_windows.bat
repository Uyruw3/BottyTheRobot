@echo off
REM Botty Prototype - Windows Setup Script
REM Run this script after cloning the repository

echo ====================================
echo   Botty Prototype - Setup (Windows)
echo ====================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found!
    echo Install Python 3.12+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)
echo [OK] Python found:
python --version

REM Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Python 3.10+ recommended for best compatibility
)

REM Create virtual environment
if not exist ".venv" (
    echo [..] Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate and install
echo [..] Installing dependencies...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install -e .
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Create user data directory
if not exist "%USERPROFILE%\.botty" (
    mkdir "%USERPROFILE%\.botty"
    echo [OK] Created user data directory at %%USERPROFILE%%\.botty
)

REM Create plugins directory
if not exist "%USERPROFILE%\.botty\plugins" (
    mkdir "%USERPROFILE%\.botty\plugins"
    echo [OK] Created plugins directory
)

echo.
echo ====================================
echo   Setup Complete!
echo ====================================
echo.
echo To run Botty:
echo   .venv\Scripts\activate
echo   python -m botty
echo.
echo Or use the launcher:
echo   scripts\run_botty.ps1
echo.
pause
