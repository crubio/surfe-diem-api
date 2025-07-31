#!/usr/bin/env python3
"""
Tool to batch add NOAA buoy locations via API
Scrapes metadata from NDBC station pages and creates locations via POST /api/v1/locations

Usage:
  python tools/add_noaa_buoys.py 51001 51002 51003
  python tools/add_noaa_buoys.py 51001 --token YOUR_JWT_TOKEN
  ENVIRONMENT=production python tools/add_noaa_buoys.py 51001 51002 --token YOUR_JWT_TOKEN
"""

import requests
import re
import time
import json
import sys
import argparse
from bs4 import BeautifulSoup
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
PRODUCTION_URL = os.getenv('PRODUCTION_URL', 'https://api.surfe-diem.com')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')  # JWT token for admin access
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')  # 'local' or 'production'

def extract_metadata_from_station_page(station_id: str) -> Optional[Dict]:
    """
    Scrape metadata from NDBC station page
    """
    url = f"https://www.ndbc.noaa.gov/station_page.php?station={station_id}"
    
    try:
        print(f"Fetching metadata for station {station_id}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract station name and location
        title_text = soup.find('h1').get_text() if soup.find('h1') else ""
        
        # Look for station name pattern: "Station 51001 (LLNR 28006) - NORTHWESTERN HAWAII ONE"
        name_match = re.search(r'Station \d+.*? - (.+)', title_text)
        station_name = name_match.group(1).strip() if name_match else f"Station {station_id}"
        
        # Extract the full location string with degrees/minutes/seconds
        coord_text = soup.get_text()
        
        # Extract the complete location string: "24.475 N 162.030 W (24°28'30" N 162°1'48" W)"
        location_match = re.search(r'\d+\.\d+\s*[NS]\s*\d+\.\d+\s*[EW]\s*\([^)]+\)', coord_text)
        
        if location_match:
            # Use the complete location string as found
            location_str = location_match.group(0)
        else:
            # Fallback to simple decimal coordinates if full format not found
            lat_match = re.search(r'(\d+\.\d+)\s*[NS]', coord_text)
            lon_match = re.search(r'(\d+\.\d+)\s*[EW]', coord_text)
            
            if lat_match and lon_match:
                lat_decimal = lat_match.group(1)
                lon_decimal = lon_match.group(1)
                
                # Determine N/S and E/W
                lat_dir = "N" if "N" in lat_match.group(0) else "S"
                lon_dir = "W" if "W" in lon_match.group(0) else "E"
                
                location_str = f"{lat_decimal} {lat_dir} {lon_decimal} {lon_dir}"
            else:
                location_str = None
        
        # Extract description/location info
        location_info = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if 'NM' in text and ('of' in text or 'from' in text):
                location_info.append(text)
                break
        
        location_description = location_info[0] if location_info else f"NOAA Buoy Station {station_id}"
        
        # Extract water depth if available
        depth_match = re.search(r'Water depth:\s*(\d+)\s*m', coord_text)
        water_depth = depth_match.group(1) if depth_match else None
        
        if water_depth:
            location_description += f" (Water depth: {water_depth}m)"
        
        return {
            'location_id': station_id,
            'name': station_name,
            'description': location_description,
            'location': location_str,
            'url': url,
            'active': True,
            'weight': 0
        }
        
    except Exception as e:
        print(f"Error fetching metadata for station {station_id}: {e}")
        return None

def create_location_via_api(location_data: Dict, api_url: str, admin_token: str) -> bool:
    """
    Create location via API POST /api/v1/locations
    """
    headers = {
        'Authorization': f'Bearer {admin_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/v1/locations",
            json=location_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            created_location = response.json()
            print(f"✅ Created location: {created_location['name']} (ID: {created_location['id']})")
            return True
        else:
            print(f"❌ Failed to create location {location_data['location_id']}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating location {location_data['location_id']}: {e}")
        return False



def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Batch add NOAA buoy locations via API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/add_noaa_buoys.py 51001 51002 51003
  python tools/add_noaa_buoys.py 51001 --token YOUR_JWT_TOKEN
  ENVIRONMENT=production python tools/add_noaa_buoys.py 51001 51002 --token YOUR_JWT_TOKEN
        """
    )
    
    parser.add_argument(
        'buoy_ids',
        nargs='+',
        help='NOAA buoy station IDs to add (e.g., 51001 51002 51003)'
    )
    
    parser.add_argument(
        '--token',
        type=str,
        help='JWT admin token (overrides ADMIN_TOKEN environment variable)'
    )
    
    return parser.parse_args()

def main():
    """
    Main function to batch add NOAA buoy locations
    """
    # Parse command line arguments
    args = parse_arguments()
    buoy_ids = args.buoy_ids
    token_override = args.token
    
    print("🚢 NOAA Buoy Location Batch Adder")
    print("=" * 50)
    
    # Determine which API URL to use
    if ENVIRONMENT == 'production':
        api_url = PRODUCTION_URL
        print("🌐 Running against PRODUCTION environment")
    else:
        api_url = API_BASE_URL
        print("🏠 Running against LOCAL environment")
    
    # Use token from command line or environment variable
    admin_token = token_override or ADMIN_TOKEN
    
    if not admin_token:
        print("❌ Error: No admin token provided")
        print("Please provide a JWT token using --token or set ADMIN_TOKEN environment variable")
        print("\nTo get an admin token:")
        print(f"curl -X POST '{api_url}/api/v1/login' \\")
        print("  -H 'Content-Type: application/x-www-form-urlencoded' \\")
        print("  -d 'username=your_admin_email&password=your_password'")
        return
    
    print(f"📡 API URL: {api_url}")
    print(f"🎯 Adding {len(buoy_ids)} buoy locations...")
    print(f"📋 Buoy IDs: {', '.join(buoy_ids)}")
    print()
    
    success_count = 0
    error_count = 0
    
    for i, buoy_id in enumerate(buoy_ids, 1):
        print(f"[{i}/{len(buoy_ids)}] Processing buoy {buoy_id}...")
        
        # Extract metadata from NDBC page
        metadata = extract_metadata_from_station_page(buoy_id)
        
        if not metadata:
            print(f"❌ Failed to extract metadata for buoy {buoy_id}")
            error_count += 1
            continue
        
        # Debug: Print the metadata being sent
        print(f"📋 Metadata for {buoy_id}: {json.dumps(metadata, indent=2)}")
        
        # Create location via API
        if create_location_via_api(metadata, api_url, admin_token):
            success_count += 1
        else:
            error_count += 1
        
        # Rate limiting - be nice to NDBC servers
        time.sleep(1)
        print()
    
    print("=" * 50)
    print(f"✅ Successfully added: {success_count} locations")
    print(f"❌ Failed: {error_count} locations")
    print(f"📊 Total processed: {len(buoy_ids)} locations")

if __name__ == "__main__":
    main() 