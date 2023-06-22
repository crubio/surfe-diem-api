from typing import List, Union, Optional
import json

from fastapi import Depends, FastAPI, HTTPException, Response, status, APIRouter
from sqlalchemy import func
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, oauth2
from ..schemas import (Location, LocationPost, LocationResponse, LocationPut)

router = APIRouter(
    prefix="/api/v1",
    tags=["Locations"]
)

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db), limit: int = 10, search: Optional[str] = ""):
    locations = db.query(models.Location).filter(models.Location.name.contains(search)).limit(limit).all()
    return locations

@router.get("/locations/spots", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db), limit: int = 10, current_user: int = Depends(oauth2.get_current_user)):
    '''Get a list of saved locations'''
    # locations = db.query(models.Location).limit(limit).all()
    spots = db.query(
        models.Location, func.count(models.Location.id)
    ).join(
        models.UserLocation, models.UserLocation.location_id == models.Location.id, isouter=True
    ).where(
        models.UserLocation.user_id == current_user.id
    ).group_by(
        models.Location.id
    ).limit(
        limit
    ).all()
    return spots

@router.get("/locations/spots/count")
def count_locations(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    spots = db.query(
        func.count(models.UserLocation.user_id)
    ).where(
        models.UserLocation.user_id == current_user.id
    ).group_by(
        models.UserLocation.location_id, models.UserLocation.user_id
    ).count()
    return {"count": spots}

@router.get("/locations/{id}", response_model=LocationResponse)
def get_location(id: str, db: Session = Depends(get_db)):
    '''Get by location_id'''
    # TODO: get by location id
    location = db.query(models.Location).filter(models.Location.id == id).first()

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {id} not found")
    return location

# should be an admin only route - add later
@router.post("/locations", status_code=status.HTTP_201_CREATED, response_model=LocationResponse)
def create_location(location: LocationPost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''Create a location & return the new location'''
    new_location = models.Location(creator_id=current_user.id, **location.dict())
    db.add(new_location)
    try:
        db.commit()
        db.refresh(new_location)
    except (SQLAlchemyError, DBAPIError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="something went wrong, please try again", message=f"{e}")
    
    return new_location

# should be an admin only route - add later
@router.delete("/locations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(id: str, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    '''Delete a location'''
    location_query = db.query(models.Location).filter(models.Location.id == id)
    location = location_query.first()

    if location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location '{id}' not found")

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # consider sync strategy here
    location_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# should be an admin only route - add later
@router.put("/locations/{id}", response_model=LocationResponse)
def update_location(id: int, updated_location: LocationPut, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    '''update a location based on location id'''
    query = db.query(models.Location).filter(models.Location.id == id)
    current_location = query.first()

    if current_location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location id: {id} not found")

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query.update(updated_location.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return query.first()
