from pydantic import BaseModel, EmailStr, conint, ConfigDict
from typing import Optional, List, Dict, Any
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
    '''Summary of NOAA latest observation txt feed'''
    wave_height: Optional[str]
    peak_period: Optional[str]
    water_temp: Optional[str]
    atmospheric_pressure: Optional[str]
    air_temp: Optional[str]
    dew_point: Optional[str]
    swell_height: Optional[str]
    period: Optional[str]
    direction: Optional[str]
    wind_wave_height: Optional[str]

    class Config:
        orm_mode = True

# Spots
class SpotLocationPost(BaseModel):
    '''Schema for creating a new surf spot'''
    name: str
    timezone: str
    latitude: float
    longitude: float
    subregion_name: str

class SpotLocationResponse(BaseModel):
    '''Our base schema for surf spots'''
    id: int
    name: str
    timezone: str
    latitude: float
    longitude: float
    subregion_name: str
    slug: Optional[str] = None
    
    class Config:
        orm_mode = True

# Users
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    date_created: datetime
    
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

# Batch Forecast
class BatchForecastRequest(BaseModel):
    """Request model for batch forecast endpoint"""
    model_config = ConfigDict(extra='forbid')
    
    buoy_ids: Optional[List[str]] = []
    spot_ids: Optional[List[int]] = []

class BatchForecastResponse(BaseModel):
    """Response model for batch forecast endpoint"""
    buoys: List[Dict[str, Any]]
    spots: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    