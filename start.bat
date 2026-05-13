@echo off
echo Starting Cognitia...

REM Start backend in new window
start "Cognitia Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8003"

REM Wait a sec for backend to boot
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "Cognitia Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

REM Wait for frontend to be ready
timeout /t 4 /nobreak >nul

REM Open browser
start http://localhost:5173

echo Cognitia is running!
echo Backend: http://localhost:8003/docs
echo Frontend: http://localhost:5173
echo.
echo Close the two terminal windows to stop.
pause