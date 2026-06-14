@echo off
setlocal
cd /d "%~dp0\.."

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment "venv" not found.
    echo Please create it first using: python -m venv venv
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Launching ErgoTerm...
python main.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)
