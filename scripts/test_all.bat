@echo off
echo ========================================================
echo  ChainSleuth - Comprehensive Automated Test Suite
echo ========================================================
echo.

echo [1/3] Running Smart Contract Tests (Hardhat)...
cd contracts
call npx hardhat test
if %errorlevel% neq 0 (
    echo [ERROR] Contract tests failed!
    exit /b %errorlevel%
)
cd ..

echo.
echo [2/3] Running Backend Tests (Pytest)...
set PYTHONPATH=backend
call backend\.venv\Scripts\pytest backend/tests -v
if %errorlevel% neq 0 (
    echo [ERROR] Backend tests failed!
    exit /b %errorlevel%
)

echo.
echo [3/3] Running Frontend Typecheck and Production Build (Vite)...
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed!
    exit /b %errorlevel%
)
cd ..

echo.
echo ========================================================
echo  ALL TESTS AND BUILDS PASSED SUCCESSFULLY (100%%)
echo ========================================================
