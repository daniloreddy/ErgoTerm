@echo off
setlocal
cd /d "%~dp0.."

if not exist "venv\Scripts\python.exe" (
    echo ==^> Creating virtual environment "venv"...
    python -m venv venv || exit /b 1
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\pip.exe install -r requirements.txt -r requirements.dev.txt || exit /b 1
)

call venv\Scripts\activate.bat

echo ==^> ruff format (check)
python -m ruff format --check ergo_api_client.py main.py test_api_client.py
if errorlevel 1 exit /b 1

echo ==^> ruff check
python -m ruff check ergo_api_client.py main.py test_api_client.py
if errorlevel 1 exit /b 1

echo ==^> mypy
python -m mypy ergo_api_client.py main.py
if errorlevel 1 exit /b 1

echo ==^> pytest
python -m pytest test_api_client.py -v
