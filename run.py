#!/usr/bin/env python3
"""
Holy Books Facts Checker - Startup Script
This script checks dependencies and environment before starting the application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'openai',
        'sentence_transformers',
        'faiss-cpu',
        'speech_recognition'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def check_environment():
    """Check environment variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GOOGLE_API_KEY')

    if (not openai_key or openai_key == 'your_openai_api_key_here') and not gemini_key:
        print("❌ Neither OpenAI nor Gemini API key configured")
        print("Please edit .env file and add at least one API key")
        return False
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("⚠️  OpenAI API key not configured, will use Gemini or local dataset only")
    if not gemini_key:
        print("⚠️  Gemini API key not configured, will use OpenAI or local dataset only")

    print("✅ Environment variables configured")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['data', 'static/js', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def main():
    """Main startup function"""
    print("🚀 Holy Books Facts Checker - Startup Check")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Check environment
    if not check_environment():
        print("\n📝 Setup Instructions:")
        print("1. Edit the .env file")
        print("2. Add your OpenAI API key")
        print("3. Run this script again")
        sys.exit(1)
    
    print("\n✅ All checks passed!")
    print("🚀 Starting the application...")
    print("=" * 50)
    
    # Import and run the application
    try:
        from app import app
        print("🌐 Application running at: http://localhost:5000")
        print("📖 Open your browser and navigate to the URL above")
        print("🛑 Press Ctrl+C to stop the application")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
