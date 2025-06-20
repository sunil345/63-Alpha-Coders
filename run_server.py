#!/usr/bin/env python3
"""
Simple script to run the Intelligent Email Agent API server
"""

import os
import sys
import webbrowser
import time
from threading import Thread

def setup_environment():
    """Set up basic environment variables if not present"""
    env_vars = {
        'EMAIL_ADDRESS': 'demo@example.com',
        'EMAIL_PASSWORD': 'demo-password',
        'IMAP_SERVER': 'imap.gmail.com',
        'IMAP_PORT': '993',
        'USE_SSL': 'true',
        'OPENAI_API_KEY': 'demo-key',
        'DATABASE_URL': 'sqlite:///./email_agent.db',
        'DEBUG': 'true',
        'LOG_LEVEL': 'INFO'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

def open_browser():
    """Open browser with API documentation after server starts"""
    time.sleep(3)  # Wait for server to start
    
    base_url = "http://localhost:8000"
    print(f"\n🚀 Server is running at: {base_url}")
    print(f"📚 Opening API documentation...")
    
    try:
        webbrowser.open(f"{base_url}/docs")
        print(f"   ✅ Opened Swagger UI: {base_url}/docs")
    except Exception as e:
        print(f"   ❌ Could not open browser: {e}")
    
    print(f"\n📖 Available Documentation:")
    print(f"   • Swagger UI: {base_url}/docs")
    print(f"   • ReDoc: {base_url}/redoc")
    print(f"   • Dashboard: {base_url}/")
    print(f"   • Health Check: {base_url}/health")
    
    print(f"\n🔧 Configuration:")
    print(f"   • Copy 'sample.env' to '.env' and update with your credentials")
    print(f"   • Set your OpenAI API key for AI features")
    print(f"   • Configure email settings for IMAP access")
    
    print(f"\n🛑 Press Ctrl+C to stop the server")

def main():
    """Main function to start the server"""
    print("🎯 Starting Intelligent Email Agent API Server...")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Start browser opener in background
    browser_thread = Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Import and run uvicorn
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except ImportError:
        print("❌ uvicorn not found. Please install with: pip3 install uvicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 