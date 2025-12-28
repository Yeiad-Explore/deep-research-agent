#!/bin/bash

echo "========================================"
echo " Deep Research Agent - Startup Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    echo ""
    echo "Virtual environment created!"
    echo ""
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    echo ""
    echo "Dependencies installed!"
    cd ..
else
    echo "Virtual environment found."
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Please copy backend/.env.example to backend/.env"
    echo "and configure your API keys before running the application."
    echo ""
    exit 1
fi

echo ""
echo "Starting Deep Research Agent..."
echo ""
echo "Access the application at: http://localhost:8000"
echo "API Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
