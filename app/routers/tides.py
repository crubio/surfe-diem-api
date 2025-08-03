import httpx
from typing import Union
from .. import models
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import func, select
from geopy import distance
import json
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi import APIRouter, HTTPException, status

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no tide stations found")

    best = []
    for station in stations:
        station_distance = distance.distance((lat, lng), (station.latitude, station.longitude)).miles
        if station_distance < dist:
            best.append({"station_id": station.station_id, "distance": station_distance, "latitude": station.latitude, "longitude": station.longitude})
    sorted_best = sorted(best, key=lambda k: k['distance'])
    
    if not sorted_best:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="tide data not available for this location")
    
    return sorted_best[0]


"""
NOAA Tides and Currents API Documentation

Base URL: https://api.tidesandcurrents.noaa.gov/api/prod/datagetter

Example request:
GET https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?
    date=today&
    station=9414290&
    product=water_level&
    datum=MLLW&
    time_zone=gmt&
    units=english&
    application=DataAPI_Sample&
    format=xml

Parameters:
- station: NOAA station ID (e.g., 9414290 for San Diego)
- product: Data type (water_level, predictions, etc.)
- datum: Vertical reference (MLLW, NAVD88, etc.)
- time_zone: Time zone (gmt, lst_ldt, etc.)
- units: Measurement units (english, metric)
- application: Application name for tracking
- format: Response format (json, xml, csv)
- date: Date for data (today, yesterday, YYYYMMDD)
- begin_date/end_date: Date range for historical data
- interval: Data interval (hilo, h, 6, etc.)

Please see NOAA documentation for more details: https://api.tidesandcurrents.noaa.gov/api/prod/responseHelp.html
"""
@router.get("/tides/current")
def get_current_tides(station: str, date: str = "today", product: str = "water_level", datum: str = "MLLW", time_zone: str = "gmt", units: str = "english", application: str = "surfe-diem.com", format: str = "json"):
    '''Get the current tides for a given station'''
    params = {
        "station": station,
        "product": product,
        "datum": datum,
        "time_zone": time_zone,
        "units": units,
        "application": application,
        "format": format
    }

    if date:
        params["date"] = date

    try:
        r = httpx.get(tides_url, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"something went wrong, please try again. {exc.response.reason_phrase}")
    
@router.get("/tides")
def get_tides(
    station: str,
    begin_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    product: str = "predictions",
    datum: str = "MLLW",
    date: str = "today",
    time_zone: str = "lst_ldt",
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"something went wrong, please try again. {exc.response.reason_phrase}")
    