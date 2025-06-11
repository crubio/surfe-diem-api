import httpx
from typing import Union
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/v1",
    tags=["Forecast"]
)

forecast_url = "https://marine-api.open-meteo.com/v1/marine"

@router.get("/forecast")
def get_forecast(
    latitude: float, 
    longitude: float, 
    current: Union[str, None] = None,
    hourly: Union[str, None] = None, 
    daily: Union[str, None] = None,
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    forecast_days: Union[str, None] = None,
    timezone: str = "auto", 
    length_unit: str = "imperial"
    ):
    '''Get a current forecast for a given location'''
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "length_unit": length_unit
    }
    if current:
        params["current"] = current
    if hourly:
        params["hourly"] = hourly
    if daily:
        params["daily"] = daily
    if start_date:
        params["start_time"] = start_date
    if end_date:
        params["end_time"] = end_date
    if forecast_days:
        params["forecast_days"] = forecast_days

    try:
        r = httpx.get(forecast_url, params=params)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="something went wrong, please try again")