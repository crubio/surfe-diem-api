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
    