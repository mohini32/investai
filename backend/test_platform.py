#!/usr/bin/env python3
"""
InvestAI Platform Test Script
This script tests if the InvestAI platform components are working correctly
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test if all major components can be imported"""
    print("🧪 Testing InvestAI Platform Components")
    print("=" * 60)
    
    tests = []
    
    # Test core app
    try:
        from app.main import app
        print("✅ Main FastAPI app - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Main FastAPI app - FAILED: {str(e)}")
        tests.append(False)
    
    # Test database
    try:
        from app.core.database import Base, engine
        print("✅ Database configuration - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Database configuration - FAILED: {str(e)}")
        tests.append(False)
    
    # Test models
    try:
        from app.models.user import User
        from app.models.portfolio import Portfolio
        from app.models.market_data import Security, PriceData
        print("✅ Database models - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Database models - FAILED: {str(e)}")
        tests.append(False)
    
    # Test services
    try:
        from app.services.portfolio_service import PortfolioService
        from app.services.market_data_service import MarketDataService
        print("✅ Business services - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Business services - FAILED: {str(e)}")
        tests.append(False)
    
    # Test API endpoints
    try:
        from app.api.v1.endpoints import portfolios, market_data, auth
        print("✅ API endpoints - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ API endpoints - FAILED: {str(e)}")
        tests.append(False)
    
    # Test AI components
    try:
        from app.services.ai_service import AIAnalysisService
        print("✅ AI analysis service - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ AI analysis service - FAILED: {str(e)}")
        tests.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(tests)
    total = len(tests)
    print(f"📊 Test Results: {passed}/{total} components working")
    
    if passed == total:
        print("🎉 All components are working correctly!")
        print("\n🚀 Ready to start the server:")
        print("   python start_server.py")
        print("\n🌐 Once running, visit:")
        print("   • API Docs: http://localhost:8000/docs")
        print("   • ReDoc: http://localhost:8000/redoc")
        print("   • Health Check: http://localhost:8000/health")
    else:
        print("⚠️  Some components have issues. Please check the errors above.")
        print("\n💡 Common solutions:")
        print("   • Install dependencies: pip install -r requirements.txt")
        print("   • Check Python environment")
        print("   • Verify all files are present")
    
    return passed == total

def show_platform_info():
    """Show platform information"""
    print("\n🏗️  InvestAI Platform Architecture")
    print("=" * 60)
    print("📁 Project Structure:")
    print("  investai/backend/")
    print("  ├── app/")
    print("  │   ├── main.py              # FastAPI application")
    print("  │   ├── core/                # Core configuration")
    print("  │   ├── models/              # Database models")
    print("  │   ├── services/            # Business logic")
    print("  │   ├── api/v1/endpoints/    # API endpoints")
    print("  │   └── utils/               # Utilities")
    print("  ├── requirements.txt         # Dependencies")
    print("  ├── start_server.py          # Server startup")
    print("  └── test_platform.py         # This test script")
    
    print("\n🌐 API Endpoints Available:")
    endpoints = [
        "/docs - Interactive API documentation",
        "/redoc - Alternative API documentation", 
        "/health - Health check endpoint",
        "/api/v1/auth/* - Authentication endpoints",
        "/api/v1/users/* - User management",
        "/api/v1/portfolios/* - Portfolio management",
        "/api/v1/market-data/* - Market data",
        "/api/v1/ai/* - AI analysis",
        "/api/v1/goals/* - Financial goals",
        "/api/v1/risk/* - Risk management",
        "/api/v1/tax/* - Tax planning",
        "/api/v1/performance/* - Performance analytics",
        "/api/v1/social/* - Social trading"
    ]
    
    for endpoint in endpoints:
        print(f"  • {endpoint}")

def main():
    """Main test function"""
    print("🚀 InvestAI Platform Test Suite")
    print("Testing comprehensive investment management platform...")
    print()
    
    # Test component imports
    success = test_imports()
    
    # Show platform info
    show_platform_info()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Platform is ready to run!")
        print("Execute: python start_server.py")
    else:
        print("❌ Platform has issues that need to be resolved.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
