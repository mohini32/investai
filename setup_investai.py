#!/usr/bin/env python3
"""
InvestAI Setup Script
This script sets up the InvestAI platform dependencies
"""

import subprocess
import sys
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing InvestAI Dependencies")
    print("=" * 50)
    
    # Basic requirements for InvestAI
    requirements = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.23",
        "alembic>=1.12.1",
        "psycopg2-binary>=2.9.9",
        "redis>=5.0.1",
        "pydantic>=2.5.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "loguru>=0.7.2",
        "crewai>=0.1.0",
        "pandas>=2.1.4",
        "numpy>=1.24.3",
        "requests>=2.31.0",
        "aiohttp>=3.9.1",
        "python-dotenv>=1.0.0"
    ]
    
    print("Installing packages:")
    for req in requirements:
        print(f"  • {req}")
    print()
    
    try:
        # Install packages
        cmd = [sys.executable, "-m", "pip", "install"] + requirements
        
        print("🔧 Running pip install...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All packages installed successfully!")
            return True
        else:
            print("❌ Installation failed!")
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 InvestAI Platform Setup")
    print("Setting up comprehensive investment management platform...")
    print()
    
    # Install requirements
    if install_requirements():
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("  1. Run the platform: python run_investai.py")
        print("  2. Open browser: http://localhost:8000/docs")
        print("  3. Explore the API documentation")
        print("\n📚 Platform Features:")
        print("  • Portfolio Management")
        print("  • AI-Powered Analysis")
        print("  • Financial Goal Planning")
        print("  • Risk Management")
        print("  • Tax Optimization")
        print("  • Performance Analytics")
        print("  • Social Trading")
        print("  • Market Data Integration")
        return 0
    else:
        print("\n❌ Setup failed!")
        print("💡 Try running manually: pip install fastapi uvicorn sqlalchemy")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
