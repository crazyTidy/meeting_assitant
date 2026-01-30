@echo off
echo ========================================
echo   Stopping Meeting Assistant...
echo ========================================
echo.

docker-compose down

echo.
echo ========================================
echo   Services Stopped!
echo ========================================
echo.
echo To start again: run start.bat
echo ========================================
pause
