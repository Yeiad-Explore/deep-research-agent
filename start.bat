@echo off
echo ========================================
echo  Deep Research Agent - Startup Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "backend\venv\" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    echo.
    echo Virtual environment created!
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate
    pip install -r requirements.txt
    echo.
    echo Dependencies installed!
    cd ..
) else (
    echo Virtual environment found.
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo.
    echo WARNING: .env file not found!
    echo Please copy backend\.env.example to backend\.env
    echo and configure your API keys before running the application.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Deep Research Agent...
echo.
echo Access the application at: http://localhost:8000
echo API Documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
call venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
