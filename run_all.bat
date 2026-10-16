@echo off
echo Starting RealOrReel...
echo.
echo [1/2] Starting Backend...
start "RealOrReel Backend" cmd /c "cd /d %~dp0 && python backend/app.py"
echo.
echo [2/2] Opening Browser...
timeout /t 4 /nobreak > nul
start http://127.0.0.1:8000
echo.
echo Done! Browser opening at http://127.0.0.1:8000
echo Backend running in separate window. Close that window to stop.
pause
