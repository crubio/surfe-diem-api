from typing import List, Optional
import os.path

from fastapi import Depends, HTTPException, Response, status, APIRouter
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, oauth2
from ..schemas import (BuoyLocationNOAASummary, BuoyLocationPost, BuoyLocationResponse, BuoyLocationPut, BuoyLocationLatestObservation)
import json

router = APIRouter(
    prefix="/api/v1",
    tags=["Locations"]
)

@router.get("/locations", response_model=List[BuoyLocationResponse])
def get_locations(db: Session = Depends(get_db), limit: int = 100, search: Optional[str] = ""):
    filters = [models.BuoyLocation.active == True]
    select_stmt = select(
        models.BuoyLocation, models.TideStationBuoyLocation.station_id
        ).select_from(
            models.BuoyLocation
        ).join(
            models.TideStationBuoyLocation, models.BuoyLocation.location_id == models.TideStationBuoyLocation.location_id, isouter=True
        ).filter(
            *filters
        ).order_by(
            models.BuoyLocation.weight.desc()
        )

    if search:
        select_stmt = select_stmt.where(models.BuoyLocation.name.like(f"%{search}%"))
    
    select_stmt = select_stmt.limit(limit)
    location = db.execute(select_stmt).all()

    locations_list = []
    for row in location:
        row[0].station_id = row[1]
        locations_list.append(row[0])

    return locations_list

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

# TODO: Update this route to use the database when thats available for this data.
# This is a temporary solution until we can get the latest observation data from NOAA in SQLite or use Postgres again
# Contents are scraped and added to a file from tools/get_latest_obsv_rss.py
# The file only contains the most recent observation for each location
@router.get("/locations/latest-observations", response_model=List[BuoyLocationLatestObservation])
def get_latest_observations():
    '''Get a list of all latest observations from NOAA rss feed'''
    file_path = 'data/latest_observation.json'

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No latest observation data found")
    
    return(FileResponse("data/latest_observation.json"))

@router.get("/locations/{location_id}", response_model=BuoyLocationResponse)
def get_location(location_id: str, db: Session = Depends(get_db)):
    '''Get by location_id'''
    location = db.query(models.BuoyLocation).filter(models.BuoyLocation.location_id == location_id, models.BuoyLocation.active == True).first()

    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location id {location_id} not found")
    return location

@router.get("/locations/{location_id}/latest", response_model=BuoyLocationNOAASummary)
def get_location(location_id: str, db: Session = Depends(get_db)):
    '''get latest wave summary for this location id'''
    location_summary = db.query(
        models.BuoyLocationNoaaSummary
    ).filter(
        models.BuoyLocationNoaaSummary.location_id == location_id,
    ).order_by(
        models.BuoyLocationNoaaSummary.timestamp.desc()
    ).first()
    if not location_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} not found")
    return location_summary

# TODO: Update this route to use the database when thats available for this data.
# This is a temporary solution until we can get the latest observation data from NOAA in SQLite or use Postgres again
# Contents are scraped and added to a file from tools/get_latest_obsv_rss.py
# The file only contains the most recent observation for each location
@router.get("/locations/{location_id}/latest-observation", response_model=BuoyLocationLatestObservation)
def get_location_latest_observation(location_id: str):
    '''get latest observation for this location id'''
    file_path = 'data/latest_observation.json'
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No latest observation data found")
    
    with open('data/latest_observation.json') as json_file:
        data = json.load(json_file)
    result = None
    for item in data:
        if str(item['location_id']) == location_id:
            result = item
            break
    
    if result == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location {location_id} latest observations not found")
    
    return result


@router.post("/locations", status_code=status.HTTP_201_CREATED, response_model=BuoyLocationResponse)
def create_location(location: BuoyLocationPost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    '''Create a location & return the new location'''
    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    new_location = models.BuoyLocation(**location.dict())
    db.add(new_location)
    try:
        db.commit()
        db.refresh(new_location)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="something went wrong, please try again")
    
    return new_location

@router.delete("/locations/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(id: str, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    '''Delete a location'''
    location_query = db.query(models.BuoyLocation).filter(models.BuoyLocation.id == id)
    location = location_query.first()

    if location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location '{id}' not found")

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # consider sync strategy here
    location_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/locations/{id}", response_model=BuoyLocationResponse)
def update_location(id: int, updated_location: BuoyLocationPut, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    '''update a location based on location id'''
    query = db.query(models.BuoyLocation).filter(models.BuoyLocation.id == id)
    current_location = query.first()

    if current_location == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"location id: {id} not found")

    if current_user.is_admin == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    query.update(updated_location.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return query.first()
