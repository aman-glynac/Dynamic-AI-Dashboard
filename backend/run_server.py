#!/usr/bin/env python3
"""
Run the AI Dashboard API server
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Check required environment variables
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  ERROR: GROQ_API_KEY environment variable is required")
        print("   Please set your Groq API key:")
        print("   export GROQ_API_KEY='your_api_key_here'")
        exit(1)
    
    print("🚀 Starting AI Dashboard API server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload enabled for development")
    print("\n" + "="*50)
    
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )