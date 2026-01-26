@echo off
REM Blockchain Setup Script for Windows
REM This script sets up and starts the local Hardhat blockchain node

echo.
echo ================================
echo Document Verification System
echo Blockchain Setup for Windows
echo ================================
echo.

cd /d "%~dp0\.."

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

echo [OK] Node.js version:
node --version
echo.

REM Install dependencies
echo [INFO] Installing blockchain dependencies...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

REM Compile smart contracts
echo [INFO] Compiling smart contracts...
call npm run compile
if %errorlevel% neq 0 (
    echo [ERROR] Failed to compile contracts
    pause
    exit /b 1
)
echo [OK] Smart contracts compiled successfully
echo.

REM Start Hardhat node
echo [INFO] Starting local Hardhat blockchain...
start "Hardhat Blockchain Node" cmd /k npm run node
echo [OK] Blockchain node starting in new window...
echo [INFO] RPC URL: http://localhost:8545
echo.

REM Wait for node to be ready
echo [INFO] Waiting for blockchain node to be ready...
timeout /t 10 /nobreak >nul

REM Deploy contracts
echo [INFO] Deploying smart contracts...
call npm run deploy
if %errorlevel% neq 0 (
    echo [ERROR] Failed to deploy contracts
    pause
    exit /b 1
)

echo.
echo ================================
echo Setup Completed Successfully!
echo ================================
echo.
echo Next Steps:
echo   1. Blockchain is running at http://localhost:8545
echo   2. Contract is deployed and ready to use
echo   3. Start backend: cd backend ^&^& python app/main.py
echo   4. Start frontend: cd frontend ^&^& npm start
echo.
echo To stop the blockchain, close the Hardhat window.
echo.
pause
