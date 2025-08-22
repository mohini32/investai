#!/usr/bin/env python3
"""
InvestAI Server Runner
This script properly sets up the Python path and starts the server
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so 'app' module can be found
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Now we can import and run the server
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting InvestAI Server")
    print("=" * 50)
    print(f"📁 Working directory: {current_dir}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs will be at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure you're in the investai/backend directory")
        print("2. Install dependencies: pip install fastapi uvicorn")
        print("3. Check if the 'app' folder exists in current directory")
