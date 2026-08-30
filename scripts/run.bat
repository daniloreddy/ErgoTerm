@echo off
setlocal
cd /d "%~dp0.."

if not exist "venv\Scripts\python.exe" (
    echo ==^> Creating virtual environment "venv"...
    python -m venv venv || exit /b 1
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\pip.exe install -r requirements.txt || exit /b 1
)

call venv\Scripts\activate.bat
echo Launching ErgoTerm...
python main.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)
