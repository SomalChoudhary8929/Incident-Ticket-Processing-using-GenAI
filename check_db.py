#!/usr/bin/env python3
import sqlite3
import os

def check_database():
    """Check the current database structure"""
    try:
        conn = sqlite3.connect('incidents.db')
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        print(f"Tables in database: {tables}")
        
        # Check if incidents table exists
        cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='incidents'")
        table_sql = cur.fetchone()
        
        if table_sql:
            print(f"Current incidents table structure:")
            print(table_sql[0])
        else:
            print("No incidents table found")
            
        # Check columns in incidents table
        try:
            cur.execute("PRAGMA table_info(incidents)")
            columns = cur.fetchall()
            print(f"Columns in incidents table: {columns}")
        except:
            print("Could not get column info - table might not exist")
            
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

def fix_database():
    """Fix the database structure by recreating the table with correct columns"""
    try:
        conn = sqlite3.connect('incidents.db')
        cur = conn.cursor()
        
        # Drop existing table if it exists
        cur.execute("DROP TABLE IF EXISTS incidents")
        
        # Create table with correct structure
        cur.execute("""
            CREATE TABLE incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Database structure fixed successfully")
        
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    print("🔍 Checking database structure...")
    check_database()
    
    print("\n🔧 Fixing database structure...")
    fix_database()
    
    print("\n🔍 Verifying fix...")
    check_database()
