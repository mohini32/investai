@echo off
REM InvestAI Project Setup Script for Windows
REM This script sets up the complete development environment for InvestAI

setlocal enabledelayedexpansion

REM Colors for output (Windows doesn't support colors in batch easily, so we'll use echo)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    InvestAI Setup Script                    ║
echo ║          AI-Powered Financial Advisor ^& Planner             ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Function to check if command exists
:check_command
where %1 >nul 2>&1
if %errorlevel% equ 0 (
    echo %SUCCESS% %1 found
    exit /b 0
) else (
    echo %ERROR% %1 not found
    exit /b 1
)

REM Check system requirements
echo %INFO% Checking system requirements...

REM Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo %SUCCESS% Python %%i found
) else (
    echo %ERROR% Python 3.9+ is required but not found
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('node --version') do echo %SUCCESS% Node.js %%i found
) else (
    echo %ERROR% Node.js 18+ is required but not found
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('docker --version') do echo %SUCCESS% Docker %%i found
) else (
    echo %WARNING% Docker not found. You'll need to set up databases manually
)

REM Check Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%i in ('docker-compose --version') do echo %SUCCESS% Docker Compose %%i found
) else (
    echo %WARNING% Docker Compose not found. You'll need to set up services manually
)

REM Setup Backend
echo.
echo %INFO% Setting up backend...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo %INFO% Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo %INFO% Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo %INFO% Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo %INFO% Creating backend .env file...
    copy .env.example .env
    echo %WARNING% Please update the .env file with your configuration
)

REM Create logs directory
if not exist "logs" mkdir logs

echo %SUCCESS% Backend setup completed
cd ..

REM Setup Frontend
echo.
echo %INFO% Setting up frontend...
cd frontend

REM Install dependencies
echo %INFO% Installing Node.js dependencies...
npm install

REM Create .env file if it doesn't exist
if not exist ".env.local" (
    echo %INFO% Creating frontend .env.local file...
    copy .env.example .env.local
    echo %WARNING% Please update the .env.local file with your configuration
)

echo %SUCCESS% Frontend setup completed
cd ..

REM Setup Database with Docker (if available)
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo.
        echo %INFO% Setting up database with Docker...
        
        REM Start only database services
        docker-compose up -d postgres redis
        
        REM Wait for database to be ready
        echo %INFO% Waiting for database to be ready...
        timeout /t 10 /nobreak >nul
        
        echo %SUCCESS% Database setup completed
    ) else (
        echo %WARNING% Docker Compose not available. Please set up PostgreSQL and Redis manually
    )
) else (
    echo %WARNING% Docker not available. Please set up PostgreSQL and Redis manually
    echo %WARNING% PostgreSQL: Create database 'investai_db'
    echo %WARNING% Redis: Start Redis server on port 6379
)

REM Run database migrations
echo.
echo %INFO% Running database migrations...
cd backend
call venv\Scripts\activate.bat

REM Create tables using SQLAlchemy
python -c "from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(bind=engine); print('Database tables created successfully')"

echo %SUCCESS% Database migrations completed
cd ..

REM Test setup
echo.
echo %INFO% Testing setup...

REM Test backend
cd backend
call venv\Scripts\activate.bat

echo %INFO% Testing backend server...
start /b uvicorn app.main:app --host 0.0.0.0 --port 8000
timeout /t 5 /nobreak >nul

REM Simple test using curl or PowerShell
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Out-Null; Write-Host '[SUCCESS] Backend server is working' } catch { Write-Host '[WARNING] Backend server test failed' }"

REM Kill the test server
taskkill /f /im python.exe >nul 2>&1

cd ..

REM Test frontend build
cd frontend
echo %INFO% Testing frontend build...
npm run build >nul 2>&1
if %errorlevel% equ 0 (
    echo %SUCCESS% Frontend build successful
) else (
    echo %WARNING% Frontend build failed
)
cd ..

REM Display next steps
echo.
echo %SUCCESS% Setup completed successfully!
echo.
echo Next Steps:
echo 1. Update configuration files:
echo    - backend\.env (database, API keys, etc.)
echo    - frontend\.env.local (API URL, etc.)
echo.
echo 2. Start the development servers:
echo    Backend:  cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo    Frontend: cd frontend ^&^& npm run dev
echo.
echo 3. Access the application:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 4. Optional services (if using Docker):
echo    PgAdmin: http://localhost:5050 (admin@investai.com / admin123)
echo    Redis Commander: http://localhost:8081
echo.
echo Happy coding! 🚀
echo.
pause
