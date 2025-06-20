#!/usr/bin/env python3
"""
Intelligent Email Agent - Startup Script
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

def main():
    """Main startup function"""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print("🚀 Starting Intelligent Email Agent...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}/")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔧 Debug Mode: {debug}")
    print("-" * 50)
    
    # Check for required environment variables
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if not email_address or not email_password:
        print("⚠️  Warning: Email configuration not found!")
        print("   Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your .env file")
        print("   You can still access the dashboard and configure settings")
        print()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  Warning: OpenAI API key not found!")
        print("   AI features will be limited. Set OPENAI_API_KEY for full functionality")
        print()
    
    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if debug else "warning"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Intelligent Email Agent...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 