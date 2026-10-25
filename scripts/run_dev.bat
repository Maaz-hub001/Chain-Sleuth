@echo off
echo ========================================================
echo  ChainSleuth - Local Development Startup Script
echo ========================================================
echo.

if not exist ".env" (
    echo [INFO] Creating .env from .env.example...
    copy .env.example .env
)

echo [1/2] Starting Backend API on http://localhost:8000...
start "ChainSleuth Backend" cmd /k "set PYTHONPATH=backend && backend\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend Vite Dev Server on http://localhost:5173...
start "ChainSleuth Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo  ChainSleuth is starting!
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo ========================================================
