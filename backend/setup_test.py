#!/usr/bin/env python3
"""
Setup script for MeshAI backend testing
This will help you get ready to test the current functionality
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Not in a virtual environment. Consider using one:")
        print("   python -m venv .venv")
        print("   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    env_content = """# MeshAI Backend Configuration
# Copy this file to .env and fill in your values

# Required: Get your Gemini API key from https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your-gemini-api-key-here

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration (SQLite for development)
DATABASE_URL=sqlite:///meshai.db

# Redis Configuration (optional for development)
# REDIS_URL=redis://localhost:6379/0

# CORS Configuration
CORS_ORIGINS=http://localhost:8080,http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/meshai.log

# CrewAI Configuration
CREW_VERBOSE=True
CREW_MEMORY=True
CREW_MAX_EXECUTION_TIME=300
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY")
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_logs_directory():
    """Create logs directory"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
        print("✅ Created logs directory")
    else:
        print("✅ Logs directory exists")
    return True

def main():
    """Run setup"""
    print("🚀 MeshAI Backend Setup")
    print("=" * 40)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking virtual environment", check_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating .env file", create_env_file),
        ("Creating logs directory", create_logs_directory),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your GOOGLE_API_KEY")
    print("2. Run: python test_current_functionality.py")
    print("3. If tests pass, you're ready to continue development!")
    
    print("\n💡 Getting a Gemini API Key:")
    print("1. Go to https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the key and paste it in your .env file")
    
    return True

if __name__ == "__main__":
    main() 