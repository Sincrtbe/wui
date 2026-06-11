@echo off
REM Arranca el servidor FastAPI en localhost:9080 con system tray
cd /d %~dp0
call .venv\Scripts\activate.bat
uvicorn app.main:app --reload --host 127.0.0.1 --port 9080
pause