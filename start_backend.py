
#!/usr/bin/env python3
"""
Simple startup script for the Incident Ticket Processing Backend
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False
    return True

def start_server():
    """Start the Flask server"""
    print("🚀 Starting Flask server...")
    try:
        # Import and run the Flask app
        from UI import app
        app.run(host='127.0.0.1', port=8000, debug=True)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the correct directory and all packages are installed")
    except Exception as e:
        print(f"❌ Server startup error: {e}")

if __name__ == "__main__":
    print("🏥 Incident Ticket Processing Backend")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("UI.py"):
        print("❌ UI.py not found. Make sure you're in the correct directory.")
        sys.exit(1)
    
    # Install requirements if needed
    if not install_requirements():
        sys.exit(1)
    
    # Start the server
    start_server()
