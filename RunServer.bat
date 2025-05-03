@echo off
set PORT=8000

REM Navigate to the folder containing this script
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    pause
    exit /b
)

REM Start Python HTTP server
start "" http://localhost:%PORT%
python -m http.server %PORT%
