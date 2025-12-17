@echo off
REM Get the directory of this script
cd /d "%~dp0"

REM Set PYTHONPATH to include the backend folder
set PYTHONPATH=%~dp0backend

echo ====================================================
echo Starting All In One Server...
echo PYTHONPATH: %PYTHONPATH%
echo ====================================================

REM Run uvicorn using the virtual environment's python directly
".\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
