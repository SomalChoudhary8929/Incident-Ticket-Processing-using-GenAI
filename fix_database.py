#!/usr/bin/env python3
"""
Database structure fix script
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        database=os.environ.get("PGDATABASE", "incidents"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", "")
    )

def check_table_structure():
    """Check the current table structure"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'incident' 
            AND table_name = 'ps_incidents'
            ORDER BY ordinal_position;
        """)
        
        columns = cur.fetchall()
        print("Current table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
        
        cur.close()
        conn.close()
        return columns
        
    except Exception as e:
        print(f"Error checking table structure: {e}")
        return []

def fix_table_structure():
    """Fix the table structure to match our requirements"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Drop the existing table and recreate it
        print("Dropping existing table...")
        cur.execute("DROP TABLE IF EXISTS incident.ps_incidents;")
        
        # Create the correct table structure
        print("Creating new table with correct structure...")
        cur.execute("""
            CREATE TABLE incident.ps_incidents (
                id SERIAL PRIMARY KEY,
                ticket_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(100) NOT NULL,
                issue_type VARCHAR(100) NOT NULL,
                description TEXT NOT NULL,
                priority VARCHAR(20) DEFAULT 'Medium',
                status VARCHAR(20) DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Commit the changes
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table structure fixed successfully")
        
    except Exception as e:
        print(f"❌ Error fixing table structure: {e}")

def main():
    print("🔧 Database Structure Fix Tool")
    print("=" * 40)
    
    # Check current structure
    columns = check_table_structure()
    
    if columns:
        print(f"\nFound {len(columns)} columns in existing table")
        response = input("Do you want to recreate the table with the correct structure? (y/n): ")
        if response.lower() == 'y':
            fix_table_structure()
            print("\nNew table structure:")
            check_table_structure()
        else:
            print("Table structure not changed")
    else:
        print("No existing table found, creating new one...")
        fix_table_structure()

if __name__ == "__main__":
    main()
