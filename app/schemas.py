from pydantic import BaseModel, EmailStr, conint, ConfigDict, Field
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
    
# Tides Schemas
class TideStationSearchRequest(BaseModel):
    """Request schema for finding closest tide station"""
    lat: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    lng: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    dist: float = Field(default=50, gt=0, description="Search radius in miles")


class CurrentTidesRequest(BaseModel):
    """Request schema for current tides endpoint"""
    station: str = Field(..., description="NOAA station ID")
    interval: str = Field(default="hour", description="Data interval")
    date: str = Field(default="latest", description="Date for data (latest, today, YYYYMMDD)")
    product: str = Field(default="water_level", description="Data type")
    datum: str = Field(default="MLLW", description="Vertical reference")
    time_zone: str = Field(default="gmt", description="Time zone")
    units: str = Field(default="english", description="Measurement units")
    application: str = Field(default="surfe-diem.com", description="Application name")
    format: str = Field(default="json", description="Response format")


class HistoricalTidesRequest(BaseModel):
    """Request schema for historical tides endpoint"""
    station: str = Field(..., description="NOAA station ID")
    begin_date: Optional[str] = Field(None, description="Start date (YYYYMMDD)")
    end_date: Optional[str] = Field(None, description="End date (YYYYMMDD)")
    product: str = Field(default="predictions", description="Data type")
    datum: str = Field(default="MLLW", description="Vertical reference")
    date: str = Field(default="today", description="Date for data")
    time_zone: str = Field(default="gmt", description="Time zone")
    interval: str = Field(default="hilo", description="Data interval")
    units: str = Field(default="english", description="Measurement units")
    application: str = Field(default="surfe-diem.com", description="Application name")
    format: str = Field(default="json", description="Response format")


class TideStationsListRequest(BaseModel):
    """Request schema for listing tide stations"""
    limit: int = Field(default=100, ge=1, le=1000, description="Number of stations to return")
    offset: int = Field(default=0, ge=0, description="Number of stations to skip")


class TideStationDistance(BaseModel):
    """Response schema for closest tide station search"""
    station_id: str
    distance: float
    latitude: float
    longitude: float


class TideStation(BaseModel):
    """Response schema for individual tide station"""
    id: int
    station_id: str
    station_name: str
    latitude: float
    longitude: float


class TideStationsListResponse(BaseModel):
    """Response schema for list of tide stations"""
    stations: List[TideStation]
    total: int
    limit: int
    offset: int



# Spot Accuracy Rating Schemas
from enum import Enum as PyEnum

class SpotRatingEnum(PyEnum):
    accurate = "accurate"
    not_accurate = "not_accurate"

class SpotAccuracyRatingCreate(BaseModel):
    """Schema for frontend to send rating data"""
    rating: SpotRatingEnum
    forecast_json: Optional[dict] = None
    user_id: Optional[int] = None

class SpotAccuracyRatingBase(BaseModel):
    """Complete rating record with server-generated fields"""
    spot_id: int
    spot_slug: str
    rating: SpotRatingEnum
    forecast_json: Optional[dict] = None
    timestamp: datetime
    session_id: str
    ip_address: str
    user_id: Optional[int] = None

class SpotAccuracyRatingResponse(SpotAccuracyRatingBase):
    """Database model response"""
    id: int
    class Config:
        orm_mode = True
    