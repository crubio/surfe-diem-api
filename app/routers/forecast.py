import httpx
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1",
    tags=["Forecast"]
)

@router.get("/forecast")
def get_forecast(latitude: float, longitude: float, hourly: str = "wave_height", timezone: str = "America/Los_Angeles", length_unit: str = "imperial"):
    '''Get a current forecast for a given location'''
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": hourly,
        "timezone": timezone,
        "length_unit": length_unit
    }
    try:
        r = httpx.get(f"https://marine-api.open-meteo.com/v1/marine", params=params)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code}.")