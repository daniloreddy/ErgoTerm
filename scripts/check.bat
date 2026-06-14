@echo off
cd /d "%~dp0\.."

echo =^> ruff format
.\venv\Scripts\python.exe -m ruff format ergo_api_client.py main.py test_api_client.py
if errorlevel 1 exit /b 1

echo =^> ruff check
.\venv\Scripts\python.exe -m ruff check ergo_api_client.py main.py test_api_client.py
if errorlevel 1 exit /b 1

echo =^> mypy
.\venv\Scripts\python.exe -m mypy ergo_api_client.py main.py
if errorlevel 1 exit /b 1

echo =^> pytest
.\venv\Scripts\python.exe -m pytest test_api_client.py -v
