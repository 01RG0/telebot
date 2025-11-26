@echo off
echo ========================================
echo Telegram Bot Admin System - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo.
    echo Please create .env file from .env.example:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env and add your TELEGRAM_TOKEN and MONGODB_URI
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Run the application
echo.
echo ========================================
echo Starting Telegram Bot Admin System...
echo ========================================
echo.
python main.py

REM Deactivate when done
deactivate
