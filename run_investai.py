#!/usr/bin/env python3
"""
InvestAI Platform Runner
This script runs the InvestAI platform from the current directory
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the InvestAI platform"""
    print("🚀 InvestAI - Comprehensive Investment Management Platform")
    print("=" * 80)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    backend_dir = script_dir / "investai" / "backend"
    
    print(f"📁 Script directory: {script_dir}")
    print(f"📁 Backend directory: {backend_dir}")
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        print("💡 Make sure you're running this from the directory containing 'investai' folder")
        return 1
    
    # Check if main.py exists
    main_py = backend_dir / "app" / "main.py"
    if not main_py.exists():
        print("❌ main.py not found!")
        print(f"💡 Expected location: {main_py}")
        return 1
    
    print("✅ InvestAI backend found!")
    print()
    
    print("🌟 Platform Features:")
    print("  • 💼 Portfolio Management System")
    print("  • 🤖 AI Analysis & Recommendations") 
    print("  • 🎯 Financial Goal Planning")
    print("  • ⚠️ Risk Management System")
    print("  • 💰 Tax Planning & Optimization")
    print("  • 📈 Performance Analytics & Reporting")
    print("  • 👥 Social Trading & Community")
    print("  • 📊 Market Data Integration")
    print()
    
    print("🌐 Server will start on:")
    print("  • Host: localhost")
    print("  • Port: 8000")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • ReDoc: http://localhost:8000/redoc")
    print()
    
    print("🔧 Starting FastAPI server...")
    print("=" * 80)
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start the server using uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        print(f"Executing: {' '.join(cmd)}")
        print("Press Ctrl+C to stop the server")
        print("-" * 80)
        
        # Run the server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except FileNotFoundError:
        print("❌ uvicorn not found!")
        print("💡 Install it with: pip install uvicorn")
        return 1
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Make sure Python is in your PATH")
        print("  3. Check if port 8000 is available")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
