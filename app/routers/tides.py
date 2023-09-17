import httpx
from typing import Union
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
        print(r.url)
        r.raise_for_status()
        return r.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"something went wrong, please try again. {exc.response.reason_phrase}")
    