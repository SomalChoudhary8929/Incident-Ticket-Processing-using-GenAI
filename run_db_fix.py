#!/usr/bin/env python3
"""
Simple script to run the database fix from db.py
"""

import sys
import os

def main():
    print("🔧 Running Database Fix from db.py")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("db.py"):
        print("❌ db.py not found. Make sure you're in the correct directory.")
        sys.exit(1)
    
    try:
        # Import and run the database fix
        from db import fix_table_structure, check_table_structure
        
        print("Current table structure:")
        columns = check_table_structure()
        
        if columns:
            print(f"\nFound {len(columns)} columns in existing table")
            print("Fixing table structure...")
            fix_table_structure()
            print("\nNew table structure:")
            check_table_structure()
        else:
            print("No existing table found, creating new one...")
            fix_table_structure()
        
        print("\n✅ Database fix completed successfully!")
        print("🚀 You can now start the backend server:")
        print("   python UI.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
