#!/bin/bash

echo "========================================"
echo "  Meeting Assistant - Docker Deploy"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[ERROR] .env file not found!"
    echo "Please create .env file with your API keys."
    exit 1
fi

echo "[1/3] Stopping existing containers..."
docker-compose down

echo ""
echo "[2/3] Building Docker images..."
docker-compose build --no-cache

echo ""
echo "[3/3] Starting containers..."
docker-compose up -d

echo ""
echo "========================================"
echo "  Deployment Complete!"
echo "========================================"
echo ""
echo "Frontend: http://localhost"
echo "Backend:  http://localhost:8000"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "========================================"
