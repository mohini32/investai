#!/usr/bin/env python3
"""
Test script to check if all imports are working correctly
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing InvestAI Imports")
    print("=" * 50)
    
    tests = []
    
    # Test core imports
    try:
        from app.core.config import settings
        print("✅ Core config - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Core config - FAILED: {str(e)}")
        tests.append(False)
    
    # Test database
    try:
        from app.core.database import Base, engine
        print("✅ Database - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Database - FAILED: {str(e)}")
        tests.append(False)
    
    # Test models
    try:
        from app.models.user import User
        from app.models.portfolio import Portfolio
        from app.models.market_data import Security, PriceData
        print("✅ Models - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Models - FAILED: {str(e)}")
        tests.append(False)
    
    # Test services
    try:
        from app.services.market_data_service import MarketDataService
        from app.services.portfolio_service import PortfolioService
        print("✅ Services - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Services - FAILED: {str(e)}")
        tests.append(False)
    
    # Test main app
    try:
        from app.main import app
        print("✅ Main app - OK")
        tests.append(True)
    except Exception as e:
        print(f"❌ Main app - FAILED: {str(e)}")
        tests.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(tests)
    total = len(tests)
    print(f"📊 Results: {passed}/{total} imports successful")
    
    if passed == total:
        print("🎉 All imports working! Ready to start server.")
        return True
    else:
        print("⚠️ Some imports failed. Check errors above.")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
