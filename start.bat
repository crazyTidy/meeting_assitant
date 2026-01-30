@echo off
echo ========================================
echo   Meeting Assistant - Docker Deploy
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please create .env file with your API keys.
    pause
    exit /b 1
)

echo [1/3] Stopping existing containers...
docker-compose down

echo.
echo [2/3] Building Docker images...
docker-compose build --no-cache

echo.
echo [3/3] Starting containers...
docker-compose up -d

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo Frontend: http://localhost
echo Backend:  http://localhost:8000
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo ========================================
pause
