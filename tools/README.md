# Tools

Utility scripts for managing the surfe-diem API.

## add_noaa_buoys.py

Batch add NOAA buoy locations by scraping metadata from NDBC station pages and creating them via the API.

### Setup

1. **Install dependencies:**
   ```bash
   pip install beautifulsoup4 requests
   ```

2. **Set environment variables (optional):**
   ```bash
   # For local development
   API_BASE_URL=http://localhost:5000
   ADMIN_TOKEN=your_jwt_admin_token
   ENVIRONMENT=local
   
   # For production
   PRODUCTION_URL=your_production_api_url
   ADMIN_TOKEN=your_jwt_admin_token
   ENVIRONMENT=production
   ```
   
   **Or use --token argument:**
   ```bash
   python tools/add_noaa_buoys.py 51001 --token YOUR_JWT_TOKEN
   ```

3. **Get admin token:**
   ```bash
   # For local development
   curl -X POST "http://localhost:5000/api/v1/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=yourpassword"
   
   # For production
   curl -X POST "your_production_api_url/api/v1/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=yourpassword"
   ```

### Usage

```bash
# Add specific buoys (uses ADMIN_TOKEN environment variable)
python tools/add_noaa_buoys.py 51001 51002 51003

# Add single buoy with token argument
python tools/add_noaa_buoys.py 51001 --token YOUR_JWT_TOKEN

# Add Hawaiian waters
python tools/add_noaa_buoys.py 51001 51002 51003 51004 51005

# Run against production with token
ENVIRONMENT=production python tools/add_noaa_buoys.py 51001 51002 --token YOUR_JWT_TOKEN
```

### What it does

1. **Scrapes metadata** from each NDBC station page (e.g., https://www.ndbc.noaa.gov/station_page.php?station=51001)
2. **Extracts information** like:
   - Station name (e.g., "NORTHWESTERN HAWAII ONE")
   - Coordinates (latitude/longitude)
   - Location description (e.g., "188 NM NW of Kauai Island, HI")
   - Water depth
3. **Creates locations** via `POST /api/v1/locations` API endpoint
4. **Rate limits** requests to be respectful to NDBC servers

### Example Buoy Sets

Common buoy ID sets you might want to add:

**Hawaiian waters:**
```bash
python tools/add_noaa_buoys.py 51001 51002 51003 51004 51005
```

**Pacific buoys:**
```bash
python tools/add_noaa_buoys.py 51026 51027 51028 51100 51101
```

**Single buoy:**
```bash
python tools/add_noaa_buoys.py 51001
```

**All default buoys:**
```bash
python tools/add_noaa_buoys.py 51001 51002 51003 51004 51005 51026 51027 51028 51100 51101 51406 51000 51407
```

### Output

```
🚢 NOAA Buoy Location Batch Adder
==================================================
📡 API Base URL: http://localhost:5000
🎯 Adding 13 buoy locations...

[1/13] Processing buoy 51001...
Fetching metadata for station 51001...
✅ Created location: NORTHWESTERN HAWAII ONE (ID: 123)

[2/13] Processing buoy 51002...
...
```

## Other Tools

- `import_spot_json.py` - Legacy tool for importing spots from JSON (deprecated)
- `generate_spot_slugs.py` - Generate slugs for existing spots (deprecated)
- `add_slug_column.py` - Add slug column to database (deprecated)

**Note:** The legacy tools are deprecated in favor of the new API endpoints.