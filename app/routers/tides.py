import httpx
from typing import Union
from .. import models
from fastapi import Depends, HTTPException, status, APIRouter
from geopy import distance
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["Tides"]
)

# Sample request:
# https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?
#   begin_date=20250801&
#   end_date=20250831&
#   date=today&
#   station=8557863&
#   product=predictions&
#   datum=MLLW&
#   time_zone=lst_ldt&
#   interval=hilo&
#   units=english&
#   application=DataAPI_Sample&
#   format=json

tides_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

@router.get("/tides/find_closest")
def get_closest_tide_station(lat: float, lng: float, dist: float = 50, db: Session = Depends(get_db)):
    '''Get the closest tide station to a given lat & lng'''
    stations = db.query(models.TideStation.station_id, models.TideStation.latitude, models.TideStation.longitude).all()

    if not stations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tide stations found in database")

    best = []
    for station in stations:
        station_distance: float = distance.distance((lat, lng), (station.latitude, station.longitude)).miles
        if station_distance < dist:
            best.append({
                "station_id": station.station_id, 
                "distance": station_distance, 
                "latitude": station.latitude, 
                "longitude": station.longitude
            })
    sorted_best = sorted(best, key=lambda k: k['distance'])
    
    if not sorted_best:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"No tide stations found within {dist} miles of coordinates ({lat}, {lng})"
        )
    
    return sorted_best[0]


"""
NOAA Tides and Currents API Documentation

Base URL: https://api.tidesandcurrents.noaa.gov/api/prod/datagetter

Example request for /tides/current:
GET https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?
    date=today&
    station=9414290&
    product=water_level&
    datum=MLLW&
    time_zone=gmt&
    units=english&
    application=surfe-diem.com&
    format=json

Parameters for /tides/current:
- station: NOAA station ID (e.g., 9414290 for San Diego) [required]
- date: Date for data (today, yesterday, YYYYMMDD) [default: today]
- product: Data type (water_level, predictions, etc.) [default: water_level]
- datum: Vertical reference (MLLW, NAVD88, etc.) [default: MLLW]
- time_zone: Time zone (gmt, lst_ldt, etc.) [default: gmt]
- units: Measurement units (english, metric) [default: english]
- application: Application name for tracking [default: surfe-diem.com]
- format: Response format (json, xml, csv) [default: json]

Parameters for /tides (historical data):
- station: NOAA station ID [required]
- begin_date/end_date: Date range for historical data [optional]
- product: Data type [default: predictions]
- datum: Vertical reference [default: MLLW]
- date: Date for data [default: today]
- time_zone: Time zone [default: gmt]
- interval: Data interval (hilo, h, 6, etc.) [default: hilo]
- units: Measurement units [default: english]
- application: Application name [default: surfe-diem.com]
- format: Response format [default: json]

Please see NOAA documentation for more details: https://api.tidesandcurrents.noaa.gov/api/prod/responseHelp.html
"""
@router.get("/tides/current")
def get_current_tides(
    station: str,
    interval: str = "hour",
    date: str = "latest", 
    product: str = "water_level", 
    datum: str = "MLLW", 
    time_zone: str = "gmt", 
    units: str = "english", 
    application: str = "surfe-diem.com", 
    format: str = "json"
):
    '''Get the current tides for a given station'''
    params = {
        "station": station,
        "interval": interval,
        "product": product,
        "datum": datum,
        "time_zone": time_zone,
        "units": units,
        "application": application,
        "format": format,
        "date": date
    }

    try:
        r = httpx.get(tides_url, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Failed to connect to NOAA API: {exc.request.url!r}"
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=f"NOAA API error: {exc.response.reason_phrase}"
        )
    
@router.get("/tides")
def get_tides(
    station: str,
    begin_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    product: str = "predictions",
    datum: str = "MLLW",
    date: str = "today",
    time_zone: str = "gmt",
    interval: str = "hilo",
    units: str = "english",
    application: str = "surfe-diem.com",
    format: str = "json"
):
    params = {
        "station": station,
        "product": product,
        "datum": datum,
        "date": date,
        "time_zone": time_zone,
        "interval": interval,
        "units": units,
        "application": application,
        "format": format
    }

    if begin_date:
        params["begin_date"] = begin_date
    if end_date:
        params["end_date"] = end_date

    try:
        r = httpx.get(tides_url, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Failed to connect to NOAA API: {exc.request.url!r}"
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code, 
            detail=f"NOAA API error: {exc.response.reason_phrase}"
        )
    