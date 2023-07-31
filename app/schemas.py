from pydantic import BaseModel, EmailStr, conint
from typing import Optional
from datetime import datetime

# Locations
class Location(BaseModel):
    '''Our base schema for location'''
    name: str
    url: Optional[str] = None
    active: Optional[bool] = True
    description: Optional[str]
    depth: Optional[str]
    elevation: Optional[str]
    location: Optional[str]

class LocationPost(Location):
    '''Our base schema for POSTing a new location'''
    location_id: str

class LocationPut(Location):
    name: Optional[str]

class LocationResponse(LocationPost):
    '''Response shape'''
    id: int
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    
    class Config:
        orm_mode = True

# Weather Data
class LocationNOAASummary(BaseModel):
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

class LocationLatestObservation(BaseModel):
    '''Summary of NOAA latest observation rss feed'''
    id: int
    location_id: str
    timestamp: datetime
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
    