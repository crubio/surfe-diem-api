import re
import os
import sqlite3 as sql
from unidecode import unidecode
from dotenv import load_dotenv

load_dotenv()

def generate_slug(name: str) -> str:
    """
    Generate a URL-friendly slug from spot name.
    
    Args:
        name (str): The spot name to convert to a slug
        
    Returns:
        str: URL-friendly slug (lowercase, hyphens, no special chars)
        
    Example:
        "Jug Handle State Beach" -> "jug-handle-state-beach"
        "Rincon Point" -> "rincon-point"
    """
    slug = unidecode(name).lower()
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', slug)

    # Remove leading/trailing hyphens
    slug = re.sub(r'^[-]+|[-]+$', '', slug)

    # Remove consecutive hyphens
    slug = re.sub(r'[-]{2,}', '-', slug)

    return slug

def generate_unique_slug(name: str, existing_slugs: list) -> str:
    """
    Generate a unique slug, adding numbers if needed to avoid conflicts.
    
    Args:
        name (str): The spot name to convert to a slug
        existing_slugs (list): List of existing slugs to check against
        
    Returns:
        str: Unique slug that doesn't conflict with existing ones
        
    Example:
        If "malibu" exists, "Malibu" -> "malibu-2"
    """
    base_slug = generate_slug(name)
    slug = base_slug
    counter = 1

    while slug in existing_slugs:
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

def migrate_spot_slugs():
    """
    Generate slugs for all existing spots in the database.
    
    This function:
    - Queries all spots from the database
    - Generates unique slugs for spots that don't have them
    - Updates the database with the new slugs
    - Prints progress information
    """
    database = os.environ.get('SQLITE_DB')
    conn = sql.connect(database, check_same_thread=False)
    cursor = conn.cursor()
    
    try:
        # Query all spots from database
        cursor.execute("SELECT id, name, slug FROM spot_location")
        spots = cursor.fetchall()
        
        # Track existing slugs to avoid conflicts
        existing_slugs = []
        updated_count = 0
        
        # Generate slugs for spots that need them
        for spot_id, name, slug in spots:
            if not slug:
                new_slug = generate_unique_slug(name, existing_slugs)
                existing_slugs.append(new_slug)
                
                # Update the database
                cursor.execute("UPDATE spot_location SET slug = ? WHERE id = ?", (new_slug, spot_id))
                print(f"Generated slug '{new_slug}' for '{name}' (ID: {spot_id})")
                updated_count += 1
        
        # Commit changes
        conn.commit()
        print(f"Generated {updated_count} unique slugs")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting spot slug migration...")
    migrate_spot_slugs()
    print("Spot slug migration completed!") 