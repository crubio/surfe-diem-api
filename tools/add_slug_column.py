import os
from dotenv import load_dotenv
import sqlite3 as sql

load_dotenv()

def add_slug_column():
    """Add slug column to spot_location table"""
    database = os.environ.get('SQLITE_DB')
    conn = sql.connect(database, check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        # Add slug column
        cursor.execute("ALTER TABLE spot_location ADD COLUMN slug TEXT")
        conn.commit()
        print("Successfully added slug column to spot_location table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(spot_location)")
        columns = cursor.fetchall()
        slug_exists = any(col[1] == 'slug' for col in columns)
        
        if slug_exists:
            print("✓ Slug column verified")
        else:
            print("✗ Slug column not found")
            
    except sql.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Slug column already exists")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_slug_column() 