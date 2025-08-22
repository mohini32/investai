@echo off
echo 🚀 InvestAI - Comprehensive Investment Management Platform
echo ===============================================================================
echo.

echo 📁 Navigating to InvestAI backend directory...
cd /d "%~dp0investai\backend"

if not exist "app\main.py" (
    echo ❌ InvestAI backend not found!
    echo 💡 Make sure this script is in the same directory as the 'investai' folder
    pause
    exit /b 1
)

echo ✅ InvestAI backend found!
echo.

echo 🌟 Platform Features:
echo   • 💼 Portfolio Management System
echo   • 🤖 AI Analysis ^& Recommendations
echo   • 🎯 Financial Goal Planning
echo   • ⚠️ Risk Management System
echo   • 💰 Tax Planning ^& Optimization
echo   • 📈 Performance Analytics ^& Reporting
echo   • 👥 Social Trading ^& Community
echo   • 📊 Market Data Integration
echo.

echo 🌐 Server will start on:
echo   • Host: localhost
echo   • Port: 8000
echo   • API Docs: http://localhost:8000/docs
echo   • ReDoc: http://localhost:8000/redoc
echo.

echo 🔧 Installing dependencies (if needed)...
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib python-multipart

echo.
echo 🔧 Starting FastAPI server...
echo ===============================================================================
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo 🛑 Server stopped
pause
