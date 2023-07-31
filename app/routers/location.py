from typing import List, Union, Optional

from fastapi import Depends, HTTPException, Response, status, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, oauth2
from ..schemas import (LocationNOAASummary, LocationPost, LocationResponse, LocationPut, LocationLatestObservation)

router = APIRouter(
    prefix="/api/v1",
    tags=["Locations"]
)

@router.get("/locations", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db), limit: int = 10, search: Optional[str] = ""):
    locations = db.query(models.Location).filter(models.Location.name.contains(search), models.Location.active == True).limit(limit).all()
    return locations

@router.get("/locations/spots", response_model=List[LocationResponse])
def get_locations(db: Session = Depends(get_db), limit: int = 10, current_user: int = Depends(oauth2.get_current_user)):
    '''Get a list of saved locations'''
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

@router.get("/locations/summary", response_model=List[LocationNOAASummary])
def get_locations_summary(db: Session = Depends(get_db), limit: int = 50):
    '''Get a list of the last n summaries'''
    location_summary = db.query(
        models.LocationNoaaSummary
    ).order_by(
        models.LocationNoaaSummary.timestamp.desc()
    ).limit(
        limit
    ).all()
    return location_summary

@router.get("/locations/latest-observations", response_model=List[LocationLatestObservation])
def get_latest_observations(db: Session = Depends(get_db), limit: int = 50):
    '''Get a list of all latest observations from NOAA rss feed'''
    latest_observations = db.query(
        models.LocationLatestObservation
    ).order_by(
        models.LocationLatestObservation.published.desc()
    ).limit(
        limit
    ).all()
    return latest_observations

@router.get("/locations/{location_id}", response_model=LocationResponse)
def get_location(location_id: str, db: Session = Depends(get_db)):
    '''Get by location_id'''
    location = db.query(models.Location).filter(models.Location.location_id == location_id, models.Location.active == True).first()

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location id {location_id} not found")
    return location

@router.get("/locations/{location_id}/latest", response_model=LocationNOAASummary)
def get_location(location_id: str, db: Session = Depends(get_db)):
    '''get latest wave summary for this location id'''
    location_summary = db.query(
        models.LocationNoaaSummary
    ).filter(
        models.LocationNoaaSummary.location_id == location_id,
    ).order_by(
        models.LocationNoaaSummary.timestamp.desc()
    ).first()
    if not location_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} not found")
    return location_summary

@router.get("/locations/{location_id}/latest-observation", response_model=LocationLatestObservation)
def get_location_latest_observation(location_id: str, db: Session = Depends(get_db)):
    '''get latest observation for this location id'''
    location_latest_observation = db.query(
        models.LocationLatestObservation
    ).filter(
        models.LocationLatestObservation.location_id == location_id,
    ).order_by(
        models.LocationLatestObservation.published.desc()
    ).first()
    return location_latest_observation

# should be an admin only route - add later
@router.post("/locations", status_code=status.HTTP_201_CREATED, response_model=LocationResponse)
def create_location(location: LocationPost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''Create a location & return the new location'''
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    new_location = models.Location(creator_id=current_user.id, **location.dict())
    db.add(new_location)
    try:
        db.commit()
        db.refresh(new_location)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="something went wrong, please try again")
    
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
