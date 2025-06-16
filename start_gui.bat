@echo off
REM Windows batch file to start Starfish Python GUI

echo Starting Starfish Python GUI...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

REM Run the GUI
python main.py %*

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo GUI exited with an error. Press any key to close.
    pause >nul
)
