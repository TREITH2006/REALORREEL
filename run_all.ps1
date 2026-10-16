@echo off
echo Starting RealOrReel...
echo.
echo [1/2] Starting Backend...
start "RealOrReel Backend" powershell -NoExit -Command "cd '%~dp0'; python backend/app.py"
echo.
echo [2/2] Opening Browser...
timeout /t 4 /nobreak > nul
start http://127.0.0.1:8000
echo.
echo Done!
pause
