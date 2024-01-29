import httpx
from typing import Union
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/v1",
    tags=["Weather"]
)

@router.get("/weather")
def get_current_weather(
    lat: float,
    lng: float,
):
    weather_url = f"https://marine.weather.gov/MapClick.php?lat={lat}&lon={lng}&unit=0&lg=english&FcstType=json"
    try:
        r = httpx.get(weather_url)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Not found")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail="something went wrong, please try again")
    