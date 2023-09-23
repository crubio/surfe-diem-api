from pydantic import BaseModel, EmailStr, conint
from typing import Optional
from datetime import datetime

# Forecast
class ForecastBasic(BaseModel):
    '''Basic forecast response from open-meteo.com
    See https://open-meteo.com/en/docs for more info
    '''
    latitude: float
    longitude: float
    hourly: Optional[str]
    daily: Optional[str]
    timeformat: Optional[str]
    timezone: Optional[str]
    past_days: Optional[int]
    start_date: Optional[str]
    end_date: Optional[str]
    length_unit: Optional[str]
    cell_selection: Optional[str]

# Locations
class BuoyLocation(BaseModel):
    '''Our base schema for location'''
    name: str
    url: Optional[str] = None
    active: Optional[bool] = True
    description: Optional[str]
    location: Optional[str]
    weight: Optional[int] = 0

class BuoyLocationPost(BuoyLocation):
    '''Our base schema for POSTing a new location'''
    location_id: str

class BuoyLocationPut(BuoyLocation):
    name: Optional[str]

class BuoyLocationResponse(BuoyLocationPost):
    '''Response shape'''
    id: int
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    station_id: Optional[str]
    
    class Config:
        orm_mode = True

# Weather Data
class BuoyLocationNOAASummary(BaseModel):
    '''Summary of NOAA data response'''
    id: int
    location_id: str
    timestamp: datetime
    date_created: datetime
    wvht: Optional[str]
    precipitation: Optional[str]
    wind: Optional[str]
    gust: Optional[str]
    peak_period: Optional[str]
    water_temp: Optional[str]
    swell: Optional[str]
    period: Optional[str]
    direction: Optional[str]
    wind_wave: Optional[str]
    ww_period: Optional[str]
    ww_direction: Optional[str]

    class Config:
        orm_mode = True

class BuoyLocationLatestObservation(BaseModel):
    '''Summary of NOAA latest observation rss feed'''
    location_id: str
    timestamp: str
    title: str
    href: str
    published: str
    wind_speed: Optional[str]
    dominant_wave_period: Optional[str]
    dew_point: Optional[str]
    water_temp: Optional[str]
    mean_wave_direction: Optional[str]
    wind_gust: Optional[str]
    average_period: Optional[str]
    location: Optional[str]
    wind_direction: Optional[str]
    air_temp: Optional[str]
    atmospheric_pressure: Optional[str]
    significant_wave_height: Optional[str]

    class Config:
        orm_mode = True

# Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserLocation(BaseModel):
    direction: conint(le=1)
    location_id: int

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str]
    