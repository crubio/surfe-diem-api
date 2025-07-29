from typing import List, Dict, Any, Optional
import httpx
import asyncio
import time
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import get_db
from .. import models, schemas
from ..classes import buoylatestobservation as buoy, buoylocation

# Simple in-memory cache with TTL
class SimpleCache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, timestamp, ttl = self._cache[key]
            if time.time() - timestamp < ttl:
                return data
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 900):  # 15 minutes default
        self._cache[key] = (value, time.time(), ttl)
    
    def clear(self):
        self._cache.clear()

# Global cache instance
weather_cache = SimpleCache()

router = APIRouter(
    prefix="/api/v1",
    tags=["Batch Forecast"]
)

@router.post("/batch-forecast", response_model=schemas.BatchForecastResponse)
async def get_batch_forecast(
    request:schemas.BatchForecastRequest,
    db: Session = Depends(get_db)
):
    """
    Get current forecast data for a batch of favorite buoy locations and spots.
    
    This endpoint accepts a list of buoy IDs and spot IDs, then returns:
    - For buoys: Latest observations and real-time data
    - For spots: Weather forecast and current conditions
    
    This is more efficient than making individual API calls from the frontend.
    """
    
    buoys_data = []
    spots_data = []
    errors = []
    
    # Process buoy locations - batch query
    buoy_locations = {}
    if request.buoy_ids:
        # Fetch all buoy locations in one query
        buoy_locations_query = db.query(models.BuoyLocation).filter(
            models.BuoyLocation.location_id.in_(request.buoy_ids)
        ).all()
        
        # Create a lookup dictionary
        for buoy in buoy_locations_query:
            buoy_locations[buoy.location_id] = buoy
        
        # Check for missing buoys
        for buoy_id in request.buoy_ids:
            if buoy_id not in buoy_locations:
                errors.append({
                    "id": buoy_id,
                    "type": "buoy",
                    "error": "Buoy location not found"
                })
        
        # Prepare all buoy API calls
        buoy_tasks = []
        buoy_coords = {}
        
        for buoy_id in request.buoy_ids:
            if buoy_id not in buoy_locations:
                continue
                
            try:
                buoy_location = buoy_locations[buoy_id]
                buoy_obj = buoylocation.BuoyLocation.from_obj(buoy_location)
                coords = buoy_obj.parse_location()
                buoy_coords[buoy_id] = coords
                
                # Create tasks for concurrent execution
                buoy_tasks.append((
                    buoy_id,
                    get_latest_observation_async(buoy_id),
                    get_weather_forecast_async(coords[1], coords[0])  # lat, lng
                ))
                
            except Exception as e:
                errors.append({
                    "id": buoy_id,
                    "type": "buoy",
                    "error": f"Failed to prepare buoy data: {str(e)}"
                })
        
        # Execute all buoy API calls concurrently
        if buoy_tasks:
            buoy_results = await asyncio.gather(
                *[asyncio.gather(obs_task, weather_task, return_exceptions=True) 
                  for _, obs_task, weather_task in buoy_tasks],
                return_exceptions=True
            )
            
            # Process results
            for i, (buoy_id, _, _) in enumerate(buoy_tasks):
                if isinstance(buoy_results[i], Exception):
                    errors.append({
                        "id": buoy_id,
                        "type": "buoy",
                        "error": f"Failed to fetch data: {str(buoy_results[i])}"
                    })
                    continue
                
                latest_obs, weather_forecast = buoy_results[i]
                
                # Handle exceptions from individual tasks
                if isinstance(latest_obs, Exception):
                    latest_obs = None
                if isinstance(weather_forecast, Exception):
                    weather_forecast = None
                
                buoy_location = buoy_locations[buoy_id]
                buoy_data = {
                    "id": buoy_id,
                    "name": buoy_location.name,
                    "observation": latest_obs,
                    "weather": extract_essential_weather(weather_forecast, None)
                }
                
                buoys_data.append(buoy_data)
    
    # Process spots - batch query
    spots = {}
    if request.spot_ids:
        # Fetch all spots in one query
        spots_query = db.query(models.SpotLocation).filter(
            models.SpotLocation.id.in_(request.spot_ids)
        ).all()
        
        # Create a lookup dictionary
        for spot in spots_query:
            spots[spot.id] = spot
        
        # Check for missing spots
        for spot_id in request.spot_ids:
            if spot_id not in spots:
                errors.append({
                    "id": spot_id,
                    "type": "spot",
                    "error": "Spot not found"
                })
        
        # Prepare all spot API calls
        spot_tasks = []
        
        for spot_id in request.spot_ids:
            if spot_id not in spots:
                continue
                
            try:
                spot = spots[spot_id]
                
                # Create tasks for concurrent execution
                spot_tasks.append((
                    spot_id,
                    get_weather_forecast_async(float(spot.latitude), float(spot.longitude))
                ))
                
            except Exception as e:
                errors.append({
                    "id": spot_id,
                    "type": "spot",
                    "error": f"Failed to prepare spot data: {str(e)}"
                })
        
        # Execute all spot API calls concurrently
        if spot_tasks:
            spot_results = await asyncio.gather(
                *[weather_task for _, weather_task in spot_tasks],
                return_exceptions=True
            )
            
            # Process results
            for i, (spot_id, _) in enumerate(spot_tasks):
                if isinstance(spot_results[i], Exception):
                    errors.append({
                        "id": spot_id,
                        "type": "spot",
                        "error": f"Failed to fetch data: {str(spot_results[i])}"
                    })
                    continue
                
                weather_forecast = spot_results[i]
                current_weather = None  # No longer fetching current weather
                
                # Handle exceptions from individual tasks
                if isinstance(weather_forecast, Exception):
                    weather_forecast = None
                
                # Extract only essential weather data
                essential_weather = extract_essential_weather(weather_forecast, current_weather)
                
                spot = spots[spot_id]
                spot_data = {
                    "id": spot_id,
                    "name": spot.name,
                    "slug": spot.slug,
                    "weather": essential_weather
                }
                
                spots_data.append(spot_data)
    
    return schemas.BatchForecastResponse(
        buoys=buoys_data,
        spots=spots_data,
        errors=errors
    )

@router.get("/cache/status")
async def get_cache_status():
    """Get cache status for debugging"""
    return {
        "cache_size": len(weather_cache._cache),
        "cache_keys": list(weather_cache._cache.keys())
    }

@router.post("/cache/clear")
async def clear_cache():
    """Clear the weather cache"""
    weather_cache.clear()
    return {"message": "Cache cleared"}

def extract_essential_weather(weather_forecast: Optional[Dict], current_weather: Optional[Dict]) -> Dict[str, Any]:
    """Extract only essential weather data for spots"""
    essential = {
        "swell": None,
        "wind": None,
        "current": None
    }
    
    # Extract swell data from weather forecast
    if weather_forecast and "hourly" in weather_forecast:
        hourly = weather_forecast["hourly"]
        if "wave_height" in hourly and "wave_direction" in hourly and "wave_period" in hourly:
            # Get the first available data point
            for i in range(len(hourly["wave_height"])):
                if hourly["wave_height"][i] is not None:
                    essential["swell"] = {
                        "height": hourly["wave_height"][i],
                        "direction": hourly["wave_direction"][i],
                        "period": hourly["wave_period"][i]
                    }
                    break
    
    # Extract wind data from weather forecast (if available)
    if weather_forecast and "current" in weather_forecast:
        current = weather_forecast["current"]
        if "wind_speed_10m" in current and "wind_direction_10m" in current:
            essential["wind"] = {
                "speed": current["wind_speed_10m"],
                "direction": current["wind_direction_10m"]
            }
    
    # Extract current conditions from NOAA weather
    if current_weather and "currentobservation" in current_weather:
        obs = current_weather["currentobservation"]
        essential["current"] = {
            "temperature": obs.get("Temp", None),
            "conditions": obs.get("Weather", None)
        }
    
    return essential

async def get_latest_observation_async(location_id: str) -> Optional[Dict[str, Any]]:
    """Get latest observation for a buoy location"""
    try:
        buoy_data = buoy.BuoyLatestObservation(location_id)
        async with httpx.AsyncClient() as client:
            r = await client.get(buoy_data.url(), timeout=5.0)
            r.raise_for_status()
            if r.status_code != 200:
                return None
            data = buoy_data.parse_latest_reading_data(r.text)
            return data
    except:
        return None



async def get_weather_forecast_async(lat: float, lng: float) -> Optional[Dict[str, Any]]:
    """Get weather forecast for a location"""
    # Create cache key based on coordinates (rounded to 2 decimal places for reasonable cache hits)
    cache_key = f"weather_forecast_{round(lat, 2)}_{round(lng, 2)}"
    
    # Check cache first
    cached_data = weather_cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        forecast_url = "https://marine-api.open-meteo.com/v1/marine"
        params = {
            "latitude": lat,
            "longitude": lng,
            "hourly": "wave_height,wave_direction,wave_period",
            "timezone": "auto"
        }
        
        async with httpx.AsyncClient() as client:
            r = await client.get(forecast_url, params=params, timeout=5.0)
            r.raise_for_status()
            data = r.json()
            
            # Cache the result for 15 minutes
            weather_cache.set(cache_key, data, ttl=900)
            return data
    except:
        return None



async def get_current_weather_async(lat: float, lng: float) -> Optional[Dict[str, Any]]:
    """Get current weather for a location"""
    # Create cache key based on coordinates
    cache_key = f"current_weather_{round(lat, 2)}_{round(lng, 2)}"
    
    # Check cache first
    cached_data = weather_cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        weather_url = f"https://marine.weather.gov/MapClick.php?lat={lat}&lon={lng}&unit=0&lg=english&FcstType=json"
        async with httpx.AsyncClient() as client:
            r = await client.get(weather_url, timeout=5.0)
            r.raise_for_status()
            data = r.json()
            
            # Cache the result for 10 minutes (current weather changes more frequently)
            weather_cache.set(cache_key, data, ttl=600)
            return data
    except:
        return None

 