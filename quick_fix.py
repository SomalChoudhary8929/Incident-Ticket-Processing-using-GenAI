#!/usr/bin/env python3
"""
Quick database fix script - runs automatically
"""

import subprocess
import sys
import os

def run_database_fix():
    """Run the database fix script"""
    print("🔧 Running database structure fix...")
    try:
        # Run the fix script
        result = subprocess.run([sys.executable, "fix_database.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Database fix completed successfully")
            return True
        else:
            print(f"❌ Database fix failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Database fix timed out")
        return False
    except Exception as e:
        print(f"❌ Error running database fix: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Incident Ticket Processing - Database Fix")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("fix_database.py"):
        print("❌ fix_database.py not found. Make sure you're in the correct directory.")
        sys.exit(1)
    
    # Run the fix
    if run_database_fix():
        print("\n🚀 You can now start the backend server:")
        print("   python UI.py")
    else:
        print("\n❌ Database fix failed. Please check your database connection.")
        sys.exit(1)
