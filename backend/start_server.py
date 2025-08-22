#!/usr/bin/env python3
"""
InvestAI Server Startup Script
This script starts the InvestAI FastAPI server with proper configuration
"""

import uvicorn
import sys
import os
from pathlib import Path

def main():
    """Start the InvestAI server"""
    print("🚀 Starting InvestAI - Comprehensive Investment Management Platform")
    print("=" * 80)
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    print("📊 InvestAI Platform Features:")
    print("  • Portfolio Management System")
    print("  • AI Analysis & Recommendations") 
    print("  • Financial Goal Planning")
    print("  • Risk Management System")
    print("  • Tax Planning & Optimization")
    print("  • Performance Analytics & Reporting")
    print("  • Social Trading & Community")
    print("  • Market Data Integration")
    print()
    
    print("🌐 Server Configuration:")
    print("  • Host: 0.0.0.0")
    print("  • Port: 8000")
    print("  • Reload: Enabled")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • ReDoc: http://localhost:8000/redoc")
    print()
    
    print("🔧 Starting FastAPI server...")
    print("=" * 80)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("  1. Make sure you're in the backend directory")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Check if port 8000 is available")
        print("  4. Verify Python environment is activated")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
