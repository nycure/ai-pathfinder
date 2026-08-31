@echo off
echo ==================================================
echo AI Pathfinder - Launch Sequence
echo ==================================================
echo.

echo [1/2] Starting FastAPI Backend...
start cmd /k "cd backend && call .venv\Scripts\activate 2>nul || echo Virtual env not found or not active. & uvicorn main:app --reload --port 8000"

echo [2/2] Starting Next.js Frontend...
start cmd /k "cd frontend && npm run dev"

echo.
echo Application is launching!
echo - Frontend will be available at: http://localhost:3000
echo - Backend API will be available at: http://localhost:8000
echo.
echo Two new terminal windows have opened for the backend and frontend logs.
echo Keep those windows open to use the application.
echo ==================================================
pause
